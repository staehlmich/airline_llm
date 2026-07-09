import logging
import os
import sqlite3
from operator import itemgetter
from pathlib import Path
from typing import Any, Dict

import pandas as pd
import yaml

from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool
from langchain_community.utilities import SQLDatabase
from langchain_core.chat_history import (
    BaseChatMessageHistory,
    InMemoryChatMessageHistory,
)
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class RagSystem:
    """A RAG (Retrieval Augmented Generation) system for answering questions about airline data."""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the RAG system.

        Args:
            config_path: Path to the configuration file
        """
        self.config = self._load_config(config_path)
        self.db = None
        self.rag_chain = None
        self.knowledge_base = None
        self.testset = None
        self.history_store: Dict[str, BaseChatMessageHistory] = {}

        # Check for API key
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            logger.warning("OPENAI_API_KEY not found in environment variables")

        # Automatically set up resources on initialization
        self._setup_database()
        self._create_rag_chain()
        logger.info("RagSystem initialized successfully and ready for queries!")

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from YAML file.

        Args:
            config_path: Path to the configuration file

        Returns:
            Dict containing configuration parameters
        """
        try:
            with open(config_path, "r") as file:
                config = yaml.safe_load(file)

                if not config:
                    raise ValueError(f"Configuration file '{config_path}' is empty")

            logger.info(f"Configuration loaded from {config_path}")
            return config

        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in configuration file: {e}")
            raise

    def _setup_database(self) -> None:
        """Set up the SQLite database from the CSV file."""
        csv_path = Path(self.config["data"]["csv_path"])
        db_path = Path(self.config["data"]["db_path"])
        table_name = self.config["data"]["table_name"]

        # Check if CSV file exists
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        # Read the CSV file into a pandas DataFrame
        df = pd.read_csv(csv_path)

        # Connect to SQLite database and write data
        conn = sqlite3.connect(db_path)
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        conn.close()

        # Connect to the database using LangChain
        self.db = SQLDatabase.from_uri(f"sqlite:///{db_path}")
        logger.info(f"Database setup complete. Table: {table_name}")

        # Store the dataframe for knowledge base
        self.df = df

    def _create_rag_chain(self) -> None:
        """Create the RAG chain for answering queries."""

        # Create LLM
        model_name = self.config["model"]["name"]
        temperature = self.config["model"]["temperature"]

        #Hotfix for stop-parameter error in newer models.
        #MS: removing this changes output
        original_generate = ChatOpenAI._generate

        def patched_generate(self, messages, stop=None, **kwargs):
            kwargs.pop("stop", None)
            return original_generate(self, messages, **kwargs)

        ChatOpenAI._generate = patched_generate

        llm = ChatOpenAI(
            model=model_name)

        # Add custom prompt with column descriptions
        template = """
        Given an input question, create a syntactically correct {dialect} query to run.
        Unless the user specifies in his question a specific number of examples he wishes to obtain, 
        always limit your query to at most {top_k} results.

        Here is the relevant table info:
        {table_info}

        Additional column information:
        - Flight: Unique flight number identifier (not unique per row).
        - DepartureTime: Scheduled departure time in 24-hour format (HH:MM, e.g., 19:00, 13:47)
        - Length: Flight duration in HH:MM format (e.g., 01:59, 03:43)
        - Airline: Two-letter airline code (e.g., DL=Delta, UA=United, WN=Southwest, AA=American Airlines)
        - AirportFrom: Origin airport code (3-letter IATA code, e.g., MEM, DEN, BWI)
        - AirportTo: Destination airport code (3-letter IATA code, e.g., MCO, EWR, PIT)
        - DayOfWeek: Day of the week (Mon, Tue, Wed, Thu, Fri, Sat, Sun)
        - Delay: Whether the flight is delayed (value ==  'yes')

        Question: {input}"""
        custom_prompt = ChatPromptTemplate.from_template(template)


        # Sequence: chat with history -> rewrite question -> SQL query -> execute -> answer

        # 1. History-aware question rewriter: produces a standalone question string
        rewrite_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
        You are preparing a question for a SQL database.

        Produce a standalone question by resolving references using the chat history.
        If the chat history is empty, return the user's question exactly as it is, 
        without any modifications, additions, or explanations.
        
        Preserve every entity in the question to query the database, including:
        - airport names
        - flight numbers
        - airline names
        - dates
        - departure and arrival times
        - previous constraints
        - requested changes
        
        Constraints: 
        - Flights are independent: ignore causal or comparative contexts (e.g., "considering flight X is delayed..."). 
        - Only include information that is necessary to answer the latest question.
        - Return only the rewritten question.
                    """,
                ),
                MessagesPlaceholder("history"),
                ("human", "{question}"),
            ]
        )

        rewrite_question = rewrite_prompt | llm | StrOutputParser()

        # def print_rewritten(x):
        #     print(f"[Rewriter] Rewritten question: {x['question']}")
        #     return x

        # def print_query(x):
        #     print(f"[SQL Generator] Generated SQL query: {x['query']}")
        #     return x

        # 2. NL question -> SQL query
        write_query = create_sql_query_chain(llm, self.db, prompt=custom_prompt)

        # 3. SQL query -> SQL result
        execute_query = QuerySQLDatabaseTool(db=self.db)

        # 4. SQL result -> natural language answer
        answer_prompt = ChatPromptTemplate.from_messages([
            ("system", "Given the following user question, corresponding SQL query, and SQL result, "
                       "answer the user question. If the data doesn't allow to answer the question, "
                       "reply \"I don't have the data to answer your question\"."),
            ("human", "Question: {question}\nSQL Query: {query}\nSQL Result: {result}")
        ])
        answer = answer_prompt | llm | StrOutputParser()

        chain = (
            RunnablePassthrough.assign(question=rewrite_question)
            # | RunnableLambda.assign(print_rewritten)
            | RunnablePassthrough.assign(query=write_query)
            # | RunnableLambda(print_query)
            | RunnablePassthrough.assign(result=itemgetter("query") | execute_query)
            | answer
        )

        self.rag_chain = RunnableWithMessageHistory(
            chain,
            self._get_session_history,
            input_messages_key="question",
            history_messages_key="history"
        )

        logger.info("RAG chain created successfully")

    def _get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """Get in-memory message history for a chat session."""
        if session_id not in self.history_store:
            self.history_store[session_id] = InMemoryChatMessageHistory()
        return self.history_store[session_id]

    def answer_question(self, question: str, session_id) -> str:
        """
        Answer a user question using the RAG chain.

        Args:
            question: The user's question
            session_id: Chat session identifier for persistent history

        Returns:
            The generated answer
        """

        return self.rag_chain.invoke(
                {"question": question},
                config={"configurable": {"session_id": session_id}}
        )

def main():
    """Main entry point for the application."""
    # Initialize the RAG system
    rag_system = RagSystem()

    # # Example: Multiple questions in sequence
    # questions = [
    #     "How many flights were delayed by more than 30 minutes?",
    #     "What is the average delay time for United Airlines?",
    #     "Which day of the week has the most flight cancellations?",
    #     "It is currently 11:30. What are the next 5 flights?",
    #     "It is currently 11:30. When is the next flight for AA?" #Checking time format + query with 2 variables
    # ]
    #
    # print("Multiple questions example:")
    # for question in questions:
    #     print(f"\nQuestion: {question}")
    #     answer = rag_system.answer_question(question, session_id="demo")
    #     print(f"Answer: {answer}")

    # Example: Conversational session using session-based history
    print("\n--- Conversational Example ---")

    q1 = "I'm flying from Memphis to Orlando. Is my flight delayed?"
    print(f"Question 1: {q1}")
    a1 = rag_system.answer_question(q1, session_id="demo")
    print(f"Answer: {a1}")

    q2 = "I want to fly to Fort Lauderdale instead. Which flights can I board?"
    print(f"\nQuestion 2: {q2}")
    a2 = rag_system.answer_question(q2, session_id="demo")
    print(f"Answer: {a2}")
    print(f"History after a2: {rag_system._get_session_history('demo').messages}")

if __name__ == '__main__':
    main()