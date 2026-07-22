# Changelog
The main architectural progression was:
```
Fine-tuning
    ↓
Context in prompt
    ↓
Retrieval-Augmented Generation (RAG)
```
---
## [v1.0.0](https://github.com/staehlmich/airline-rag/releases/tag/v1.0.0) — OpenAI Fine-Tuning Approach (2023)

Our initial approach utilized OpenAI's fine-tuning capabilities to create a specialized model for airline delay analysis. This method involved:

### Approach
1. Creating a custom dataset of airline delay Q&A pairs.
2. Fine-tuning the OpenAI base model on this domain-specific data.
3. Deploying the fine-tuned model to answer queries about airline delays.

### Limitations
Fine-tuning with structured data lead to poor results. 
Another downside of this approach is that the model required retraining for up-to-date answers. 

As an alternative strategy, we provided the dataset directly in the prompts. 
One disadvantage of this strategy are higher costs in comparison to the fine-tuning approach. 
This improved flexibility but was limited by context window constraints and lacked sophistication in retrieval.
Qualitative evaluation showed that the accuracy of the answer was quite low. 

---

## [v2.0.0](https://github.com/staehlmich/airline-rag/releases/tag/v2.0.0) — RAG System (since 2025)

The project evolved from a fine-tuned model into a Retrieval-Augmented
Generation (RAG) system built with [LangChain](https://www.langchain.com/).

### Approach
- **Vector Database**: Airline data is transformed into an SQL database.
- **Advanced Retrieval**: LLM is used to transform user question into an SQL query, that is passed to the database and back. 
LLM rewrites output to natural language before answering the user.
- **Evaluation Framework**: Comprehensive metrics provided by [Giskard](https://giskard.ai/) to systematically measure accuracy and relevance in model responses

### Limitations

- Giskard's [RAG Evaluation Toolkit](https://legacy-docs.giskard.ai/en/stable/open_source/testset_generation/testset_generation/index.html) allows to measure different compnents of the RAG system,
but in practice it's not so easy to always identify and separate these.
- RAG system does not support chat history.