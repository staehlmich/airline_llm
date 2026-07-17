"""
Backend entry point for developers to run the RAG system.

This script demonstrates the explicit flow:
    config.yaml → models.py → RagSystem → queries
"""

import logging
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

from backend.models import create_chat_model
from backend.rag import RagSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: Path) -> dict:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to configuration file

    Returns:
        Configuration dictionary
    """
    # Convert to a Path object for safer cross-platform path handling
    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found at: {path.resolve()}")
    
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    logger.info(f"Configuration loaded from {config_path}")
    return config


def main():
    """Main entry point for backend/developer usage."""
    # 1. Load environment variables (API keys)
    load_dotenv()
    logger.info("Environment variables loaded from .env")

    # Check if API key is available
    if not os.environ.get('OPENAI_API_KEY'):
        logger.error("OPENAI_API_KEY not found in environment variables!")
        logger.error("Please create a .env file with your API key.")
        return

    # 2. Load configuration
    project_root = Path(__file__).resolve().parent
    config_path = project_root / "backend" / "config.yaml"
    config = load_config(config_path)
    model_config = config["model"]

    # 3. Create LLM using models.py
    llm = create_chat_model(
        provider=model_config["provider"],
        model_name=model_config["name"],
        temperature=model_config["temperature"]
    )
    logger.info(f"LLM created: {model_config['provider']} - {model_config['name']}")

    # 4. Create RagSystem with injected LLM
    rag_system = RagSystem(llm=llm, config_path=config_path)
    logger.info("RAG system initialized")

    # # Example: Multiple questions in sequence
    # questions = [
    #     "How many flights were delayed by more than 30 minutes?", # -> Answer unsupported by data
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
    print("--- Conversational Example ---\n")

    q1 = "I'm flying from Memphis to Orlando. Is my flight delayed?"
    print(f"Question 1: {q1}")
    a1 = rag_system.answer_question(q1, session_id="demo")
    print(f"Answer: {a1}\n")

    q2 = "I want to fly to Fort Lauderdale instead. Which flights can I board?"
    print(f"Question 2: {q2}")
    a2 = rag_system.answer_question(q2, session_id="demo")
    print(f"Answer: {a2}\n")
    print(f"History after a2: {rag_system._get_session_history('demo').messages}")


    print("="*60)
    print("Session complete. History preserved in session 'demo'.")
    print("="*60)


if __name__ == '__main__':
    main()