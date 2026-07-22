# ✈️ Airline RAG

This project implements a production-ready Retrieval Augmented Generation (RAG) system for answering questions about airline flight data.
The system uses a SQL database as the knowledge source and leverages LangChain and OpenAI's models to provide responses to natural language questions about flight information.

[Live Demo] · [GitHub Release] · 

---

## Overview

This application mimics a chatbot for a commercial airline that answers questions about current flights.
The flight data is simulated by a Kaggle dataset originally used for a prediction task. You can read more about the data [here](https://github.com/staehlmich/airline-rag/blob/master/data/RAW_DATA_README.md).

This application allows passengers to ask detailed questions in natural language about scheduled flights beyond their own.
For example:
```
- Which day of the week has the most flight cancellations?"
- It is currently 11:30. What are the next 5 flights?"
- It is currently 11:30. When is the next flight for AA?
- I'm flying from Memphis to Orlando. Is my flight delayed?
```


Optional:
- Screenshot or short GIF of the application

---

## Why I Built This

Back in 2023, I wanted to learn how to fine-tune Large Language Models (LLM) with custom data from a real business-application.
As the technology around LLMs evolved, so did this project.
You can read about the different stages of this project in CHANGELOG.md. 
The code of the previous releases is archived under [tags](https://github.com/staehlmich/airline-rag/tags).

I wanted to get hands-on experience with RAG pipelines, as well as deploying a production-ready application.

Unlike most RAG-applications, this one uses structured data to answer user questions. 
The structured data is the kaggle dataset, which is turned into an SQL Database.
An LLM is used to transform user questions into SQL queries.

---

## Features

- **Chat History**: A session is initialized on startup, which stores chat history for better inference.
- **BYOK**: 'Bring your Own Key' allows you to run the application  using either the front or backend. Currently, only api-keys from OpenAI are supported.
- **API**: Exposes the RAG pipeline through a FastAPI backend, enabling programmatic interaction with the application.
- **Evaluation**: Run `/scripts/eval.py` to evaluate the RAG-system with the [Giskard](https://github.com/Giskard-AI/giskard-oss) framework. 
- **Configuration Management**: Configuration file `/backend/config.yaml` keeps setup of models and paths centralized.

---

## How It Works

Briefly describe the user workflow:

1. User asks questions via frontend
2. API starts session with api-key and starts an instance of RagSystem
3. RAG Pipeline uses LLM provider to include chat history if available and rewrites to standalone question.
4. RAG Pipeline passes rewritten question to LLM provider to transform into SQL query.
5. LLM provider generates answer with results of SQL query
5. Answer of Rag Pipeline is returned to the user via API.

Optional architecture diagram:

```text
[User]
   ↓
[Frontend]
   ↓
[FastAPI Backend]
   ↓
[RAG Pipeline]
   ↓
[FastAPI Backend]
   ↓
[Frontend]
   ↓
[User]
```

---
## Project Structure
```
airline-rag/
├── .gitignore                      
├── README.md                       # Project documentation
├── CHANGELOG.md                    # Project evolution
├── requirements.txt                
├── run.py                          # Main entry point
├── backend/
│   ├── config.yaml                 # Configuration settings
│   ├── main.py                     # API server
│   ├── models.py                   # Data models
│   └── rag.py                      # RAG implementation
├── data/
│   ├── RAW_DATA_README.md          
│   ├── airlines_delay.csv          # Complete dataset
│   ├── airlines_delay_sample.csv   
│   ├── airlines_delay_sample.db    # SQLite database
│   └── testset.json                # Test dataset for replicaion of results
├── evaluation/                     # Latest evaluation results
│   └── evaluation_v3.0.0.html       
├── frontend/
│   ├── index.html                  # HTML interface
│   └── app.js                      # JavaScript application
└── scripts/
    ├── eval.py                     # Evaluation script
    └── preprocessing.py            # Data preprocessing
```
---

## Backend usage and replicate steps
If you install this repository to run locally you need to: 
1. Set your OpenAI api-key in the `.env` file.
2. Run `/scripts/preprocessing.py` to create a neww sample dataset.
3. You can run the model with `run.py`.
4. Evaluation 
   5. Run `pip install giskard==2.16.2` for the additional requirements. 
   6. run `/scripts/eval.py`. You can generate a new `testset.json`. 
   7. View the latest evaluation results in the `/evaluation` folder.


## Future features & fixes
- [ ] Support different models (Gemini, Anthropic, etc.).
- [ ] Improved Path Handling.
- [ ] Expand separation of concerns for better maintenance.
- [ ] Rag Pipeline: Add Query decomposition to handle multi-part questions.
- [ ] Evaluation: Implement RAGAs.
- [ ] Evaluation: Implement LLM as a Judge.