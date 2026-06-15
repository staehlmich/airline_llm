import logging
import os
import sqlite3
from operator import itemgetter
from pathlib import Path
from typing import Dict, Any, Optional

import pandas as pd
import yaml
# Import Giskard for evaluation
from giskard.rag import KnowledgeBase, generate_testset, evaluate, QATestset
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai.chat_models import ChatOpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from YAML file.

        Args:
            config_path: Path to the configuration file

        Returns:
            Dict containing configuration parameters
        """
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                logger.info(f"Configuration loaded from {config_path}")
                return config
        #TODO: Probably unnecessary.
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            # Fallback to default configuration
            return {
                "data": {
                    "csv_path": "data/airlines_delay_sample.csv",
                    "db_path": "airlines_delay_sample.db",
                    "table_name": "AirlinesDelay"
                },
                "model": {
                    "name": "gpt-3.5-turbo",
                    "temperature": 0
                },
                "evaluation": {
                    "num_questions": 60,
                    "agent_description": "A chatbot answering questions about flights",
                    "report_path": "report.html"
                }
            }

    def setup_database(self) -> None:
        """Set up the SQLite database from the CSV file."""
        try:
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

        except Exception as e:
            logger.error(f"Database setup failed: {e}")
            raise

    def create_rag_chain(self) -> None:
        """Create the RAG chain for answering queries."""
        try:
            if self.db is None:
                raise ValueError("Database not initialized. Call setup_database() first.")

            # Check for API key
            api_key = os.environ.get('OPENAI_API_KEY')
            if not api_key:
                logger.warning("OPENAI_API_KEY not found in environment variables")

            # Create LLM
            model_name = self.config["model"]["name"]
            temperature = self.config["model"]["temperature"]
            llm = ChatOpenAI(model=model_name, temperature=temperature)

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
            - Delay: Whether the flight is delayed (values: 'yes' or 'no')
            
            Question: {input}"""
            custom_prompt = PromptTemplate.from_template(template)


            # Create tools
            execute_query = QuerySQLDataBaseTool(db=self.db)
            write_query = create_sql_query_chain(llm, self.db, prompt=custom_prompt)

            # Create prompt
            answer_prompt = PromptTemplate.from_template(
                """Given the following user question, corresponding SQL query, and SQL result, answer the user question. 
                If the data doesn't allow to answer the question, reply "I don't have the data to answer your question".

                Question: {question}
                SQL Query: {query}
                SQL Result: {result}
                Answer: """
            )

            # Build chain
            answer = answer_prompt | llm | StrOutputParser()
            self.rag_chain = (
                    RunnablePassthrough.assign(query=write_query).assign(
                        result=itemgetter("query") | execute_query
                    )
                    | answer
            )

            logger.info("RAG chain created successfully")

        except Exception as e:
            logger.error(f"Failed to create RAG chain: {e}")
            raise

    def answer_question(self, question: str, history: Optional[list] = None) -> str:
        """
        Answer a user question using the RAG chain.

        Args:
            question: The user's question
            history: Optional conversation history

        Returns:
            The generated answer
        """
        if self.rag_chain is None:
            raise ValueError("RAG chain not initialized. Call create_rag_chain() first.")

        try:
            return self.rag_chain.invoke({"question": question})
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return "I'm sorry, I couldn't process your question."

    def _setup_evaluation(self) -> None:
        """Set up knowledge base and test set for evaluation."""
        try:
            if self.df is None:
                raise ValueError("DataFrame not initialized. Call setup_database() first.")

            self.knowledge_base = KnowledgeBase(self.df)
            testset_path = "testset.json"

            if os.path.exists(testset_path):
                logger.info(f"Loading existing test set from {testset_path}")
                self.testset = QATestset.load(testset_path)
            else:
                num_questions = self.config["evaluation"]["num_questions"]
                agent_description = self.config["evaluation"]["agent_description"]

                self.testset = generate_testset(
                    self.knowledge_base,
                    num_questions=num_questions,
                    agent_description=agent_description,
                )
                self.testset.save(testset_path)
                logger.info(f"New test set created and saved to {testset_path}")

        except Exception as e:
            logger.error(f"Failed to setup evaluation: {e}")
            raise

    def run_evaluation(self) -> None:
        """Run the evaluation on the test set and generate a report."""
        try:
            # Automatically set up evaluation if it hasn't been done yet
            if self.testset is None or self.knowledge_base is None:
                logger.info("Evaluation components not found. Initializing setup...")
                self._setup_evaluation()

            def answer_fn(question, history=None):
                return self.answer_question(question, history)

            report = evaluate(answer_fn, testset=self.testset, knowledge_base=self.knowledge_base)

            report_path = self.config["evaluation"]["report_path"]
            report.to_html(report_path)

            logger.info(f"Evaluation complete. Report saved to {report_path}")

        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            raise


def main():
    """Main entry point for the application."""
    try:
        # Initialize the RAG system
        rag_system = RagSystem()

        # Setup the database
        rag_system.setup_database()

        # Create the RAG chain
        rag_system.create_rag_chain()

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
        #     answer = rag_system.answer_question(question)
        #     print(f"Answer: {answer}")

        # Run evaluation with automatic setup. Reuse Giskard generated test set if available.
        rag_system.run_evaluation()

        # logger.info("RAG system evaluation completed successfully")

    except Exception as e:
        logger.error(f"An error occurred in the main function: {e}")
        raise


if __name__ == '__main__':
    main()