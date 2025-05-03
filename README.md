# RAG Implementation for Airline Data

## Overview

This branch introduces a production-ready implementation of Retrieval Augmented Generation (RAG) for answering questions about airline flight data. The system uses a SQL database as the knowledge source and leverages LangChain and OpenAI's models to provide accurate responses to natural language queries about flight information.

## Features

- **Modular Architecture**: Code organized into a well-structured class with clear responsibilities
- **Database Integration**: Uses SQLite to store and query flight data
- **Configuration Management**: External YAML configuration for easy customization
- **Robust Error Handling**: Comprehensive error handling and logging
- **Evaluation Framework**: Integration with Giskard for automated RAG system evaluation
- **Interactive Q&A**: Support for answering individual questions or running in interactive mode

## Requirements

- Python 3.8+
- OpenAI API key (set as environment variable `OPENAI_API_KEY`)
- Required packages (see `requirements.txt`)

## Project Structure

```
.
├── config.yaml              # Configuration settings
├── rag_fly.py            # Main RAG implementation
├── data/                    # Data directory
│   └── airlines_delay_sample.csv  # Flight delay dataset
├── requirements.txt         # Project dependencies
└── README.md                # This documentation
```


## Configuration

The system is configured through a YAML file (`config.yaml`) with the following structure:

```yaml
data:
  csv_path: "data/airlines_delay_sample.csv"
  db_path: "airlines_delay_sample.db"
  table_name: "AirlinesDelay"

model:
  name: "gpt-3.5-turbo"
  temperature: 0

evaluation:
  num_questions: 60
  agent_description: "A chatbot answering questions about flights"
  report_path: "report.html"
```


## Usage Examples

### Basic Usage

```python
from rag_fly import RagSystem

# Initialize the system
rag = RagSystem()
rag.setup_database()
rag.create_rag_chain()

# Ask a question
answer = rag.answer_question("Which airline has the most delays?")
print(f"Answer: {answer}")
```


### Running Multiple Queries

```python
questions = [
    "How many flights were delayed by more than 30 minutes?",
    "What is the average delay time for United Airlines?",
    "Which day of the week has the most flight cancellations?"
]

for question in questions:
    print(f"\nQuestion: {question}")
    answer = rag.answer_question(question)
    print(f"Answer: {answer}")
```


### Interactive Mode

```python
print("Interactive mode. Type questions or press Enter to exit.")
while True:
    question = input("\nQuestion: ")
    if not question:
        break
    answer = rag.answer_question(question)
    print(f"Answer: {answer}")
```


### Running Evaluation

```python
# Setup and run evaluation
rag.setup_evaluation()
rag.run_evaluation()
print(f"Evaluation report saved to {rag.config['evaluation']['report_path']}")
```


## How It Works

1. **Database Setup**: The system converts CSV data into a SQLite database for efficient querying
2. **RAG Chain Creation**: A LangChain-based RAG pipeline is created to:
   - Convert natural language questions to SQL queries
   - Execute SQL queries against the database
   - Format results into natural language responses
3. **Question Answering**: The system processes user questions through the RAG chain to provide answers
4. **Evaluation**: The system can generate test questions and evaluate its own performance