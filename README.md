# Airline Delay Analysis Assistant: Evolution from Fine-Tuning to RAG
## Project Overview
This repository contains an AI-powered assistant for analyzing airline delay data. The project has evolved through multiple approaches, showcasing the advancement of LLM application techniques from basic fine-tuning to RAG (Retrieval-Augmented Generation) systems.
## Evolution Timeline
### Stage 1: OpenAI Fine-Tuning Approach (v1)
Our initial approach utilized OpenAI's fine-tuning capabilities to create a specialized model for airline delay analysis. This method involved:
- Creating a custom dataset of airline delay Q&A pairs
- Fine-tuning the OpenAI base model on this domain-specific data
- Deploying the fine-tuned model to answer queries about airline delays

While this approach produced good results for standard questions within the fine-tuning dataset, it had limitations with novel queries and couldn't adapt to new data without retraining.
### Stage 2: Context-in-Prompt Approach
As an intermediate step, we explored embedding relevant context directly in prompts:
- Preprocessing the airline data into digestible chunks
- Using basic retrieval mechanisms to find relevant data for a query
- Including this data directly in the prompt sent to the LLM

This improved flexibility but was limited by context window constraints and lacked sophistication in retrieval.
Manual inspection showed that the accuracy of the answer was quite low. 
### Stage 3: RAG System (v2)
Our current implementation leverages a full Retrieval-Augmented Generation (RAG) system built with [LangChain](https://www.langchain.com/):
- **Vector Database**: Airline data is embedded and stored in a vector database for semantic search
- **Advanced Retrieval**: LangChain's query-aware chunking and hybrid search algorithms find the most relevant information
- **LLM Integration**: Retrieved content is intelligently incorporated into prompts using LangChain's chains and agents
- **Evaluation Framework**: Comprehensive metrics provided by [Giskard](https://giskard.ai/) to measure accuracy, relevance, and bias in model responses

LangChain provides the flexible framework that powers our RAG pipeline, enabling modular components that can be swapped or upgraded as needed. Giskard's evaluation suite allows us to systematically test and validate our system, ensuring reliability and identifying areas for improvement.


## Usage
### Installation
``` bash
# Clone the repository
git clone https://github.com/yourusername/airline-delay-analysis.git
cd airline-delay-analysis

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```
### Configuration
1. Create a `config.yaml` file with your API keys and settings
2. Place your airline data in the `data/` directory

### Running the RAG System
``` bash
python rag_system.py --query "What are the main causes of delays in Chicago?"
```
