#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import openai
import config
import pandas as pd
from analyze import format_dataset
import json

openai.api_key = config.OPENAI_API_KEY

def generate_prompts(df):
    """
    Function to generate completion prompts from df for fine-tuning LLM.
    :param df: pandas dataframe with airline data
    :return:
    """
    # Iterate through each row in the dataframe and create a prompt and completion pair
    prompt_completion_pairs = []
    for index, row in df.iterrows():
        prompt = f"Provide a written summary of Flight {row['Flight']}, operated by {row['Airline']}, which departed from {row['AirportFrom']} to {row['AirportTo']} on {row['DayOfWeek']} at {row['Time']} hours and had a flight length of {row['Length']} minutes."
        completion = f"Flight {row['Flight']} operated by {row['Airline']} departed from {row['AirportFrom']} to {row['AirportTo']} on {row['DayOfWeek']} at {row['Time']} hours and had a flight length of {row['Length']} minutes. The delay status was {row['Delay']}."
        prompt_completion_pairs.append(
            {"prompt": prompt, "completion": completion})

    # Export the prompt and completion pairs to a JSON file
    with open("data/prompt_completion_pairs.json", "w") as outfile:
        json.dump(prompt_completion_pairs, outfile)

if __name__ == '__main__':

    #TODO: How to create github repo from PyCharm?
    prompt = "Is flight 1558 delayed?"
    # resp = openai.Completion.create(model="text-davinci-003", prompt=prompt,
  # temperature=0)
    # print(resp["choices"][0]['text'])

    # Response without fine-tuning:
    #"\n\nIt is not possible to answer this question without more information."

    df = pd.read_csv("data/airlines_delay.csv")
    df = format_dataset(df)

    # generate_prompts(df)