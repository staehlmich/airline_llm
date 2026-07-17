import logging
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv
from giskard.rag import KnowledgeBase, QATestset, evaluate, generate_testset
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage

from backend.models import create_chat_model
from backend.rag import RagSystem

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Ensure the working directory is always the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.chdir(PROJECT_ROOT)
CONFIG_PATH = PROJECT_ROOT / "backend" / "config.yaml"

ENV_PATH = PROJECT_ROOT / ".env"

# Force load the .env file from the exact root absolute path
load_dotenv(dotenv_path=ENV_PATH)

class RagEvaluator:
    """Encapsulates all logic and callback wrapper methods for RAG system evaluations."""

    def __init__(self, rag_system: RagSystem) -> None:
        """
        Initialize the evaluator with a RAG system instance.

        :param rag_system: The instantiated RAG pipeline to be evaluated
        :type rag_system: RagSystem
        """
        self.rag_system = rag_system

    def answer_for_eval(self, question: str, history: list = None) -> str:
        """
        Callback method for Giskard to get answers from the RAG system
        while injecting Giskard's conversation history.

        :param question: The user query
        :type question: str
        :param history: List of conversation history dictionaries, defaults to None
        :type history: list, optional
        :returns: The generated response from the RAG system
        :rtype: str
        """
        session_id = "evaluation"

        # Clear previous history and populate with conversation history from the test sample
        self.rag_system.history_store[session_id] = InMemoryChatMessageHistory()
        if history:
            for msg in history:
                if msg["role"] == "user":
                    self.rag_system.history_store[session_id].add_message(
                        HumanMessage(content=msg["content"])
                    )
                elif msg["role"] == "assistant":
                    self.rag_system.history_store[session_id].add_message(
                        AIMessage(content=msg["content"])
                    )
        return self.rag_system.answer_question(question, session_id=session_id)


def main() :
    """Run the evaluation on the test set and generate a report using decoupled Giskard code."""
    # Load configuration independently
    try:
        with open(CONFIG_PATH, "r") as file:
            config = yaml.safe_load(file)
            if not config:
                raise ValueError(f"Configuration file '{CONFIG_PATH}' is empty")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise

    llm = create_chat_model(
        provider=config["model"]["provider"],
        model_name=config["model"]["name"],
        temperature=config["model"]["temperature"],
    )
    rag_system = RagSystem(llm=llm, config_path=CONFIG_PATH)
    evaluator = RagEvaluator(rag_system)

    # 1. Setup Giskard Knowledge Base and Test Set
    knowledge_base = KnowledgeBase(rag_system.df)

    # Resolve paths using local config
    testset_path = PROJECT_ROOT / config["evaluation"]["testset_path"]
    report_path = PROJECT_ROOT / config["evaluation"]["report_path"]
    results_path = PROJECT_ROOT / config["evaluation"]["results_path"]

    # 2. Create new test set or load existing one
    if testset_path.exists():
        logger.info(f"Loading existing test set from {testset_path}")
        testset = QATestset.load(str(testset_path))
    else:
        num_questions = config["evaluation"]["num_questions"]
        agent_description = config["evaluation"]["agent_description"]

        testset = generate_testset(
            knowledge_base,
            num_questions=num_questions,
            agent_description=agent_description,
        )
        testset.save(str(testset_path))
        logger.info(f"New test set created and saved to {testset_path}")

    # 3. Run evaluation passing the bounded class method
    report = evaluate(
        evaluator.answer_for_eval, testset=testset, knowledge_base=knowledge_base
    )

    report.to_html(report_path)
    print("\n--- Evaluation Results ---")
    print(report.correctness_by_question_type())

    df = report.to_pandas()
    df.to_csv(str(results_path))
    logger.info(f"Evaluation complete. Report saved to {report_path}")


if __name__ == "__main__":
    main()
