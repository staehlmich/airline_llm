# swissair_llm

This repository is an attempt to customize OPENAI's LLM to handle passenger requests regarding flight information. To simulate passenger flight information, the [airline_delays](https://www.kaggle.com/datasets/ulrikthygepedersen/airlines-delay) dataset is used.

## 1. Preprocessing and generating completion pairs
Run the script [preprocessing.py](preprocessing.py) for the following:

1. Rename columns and change the dtypes of rows.
2. Generate prompt completions pairs in JSONL format from the database to use for fine-tuning a OPENAI davinci model in step 2.
2. Write a small version of [airlines_delay.csv](data/airlines_delay.csv) of 1000 rows used in step 3.

## 2. Fine-tuning davinci LLM
Inspired by this [tutorial](https://www.youtube.com/watch?v=3EdEw4gyr-s&ab_channel=LiamOttley), we fine-tune a davinci model using the completion pairs in step 1. 
The goal is to fine-tune a model to answer questions about a database. To fine-tune a model, follow the steps on [OPENAI's page](https://platform.openai.com/docs/guides/fine-tuning).
To use the model trained for this experiment, run [llm_fly.py](llm_fly.py) from the command line:
    
    python3 llm_fly.py "Give me all information on flight 378." tuned

## 3. Prompts with context
Another strategy to customize LLMs to answer questions about a dataset, is to provide the dataset directly in the prompt.
The disadvantage of this strategy are higher costs when providing additional tokens to OPENAI's API. 
Inspired by this [notebook](https://github.com/wombyz/custom-knowledge-chatbot/blob/main/custom-knowledge-chatbot/Custom%20Knowledge%20Chatbot.ipynb), we use [LLAMA_Hub](https://github.com/emptycrown/llama-hub) tp load a small dataset and [LLAMA_INDEX](https://github.com/jerryjliu/llama_index) to generate queries which include the dataset in the prompt.
To use the script for this experiment, run llm_fly.py from the command line:
    
    python3 llm_fly.py "Give me all information on flight 378." context.