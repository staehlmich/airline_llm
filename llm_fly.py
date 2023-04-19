#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

import jsonlines
import openai
import pandas as pd
import tkinter as tk

import config
from analyze import format_dataset

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

def format_prompts(input_file: str, output_file: str):
    """
    Function to simplify the generated prompts with GPT.
    :param input_file: JSONL file containing completion pairs
    :param output_file: formatted JSONL file containing completion pairs
    :return:
    """
    # Open the input and output files
    with jsonlines.open(input_file) as reader, jsonlines.open(output_file, mode='w') as writer:
        # Iterate over each line in the input file
        for obj in reader:
            # Remove ".0" suffix from the specified fields in "prompt" and "completion"
            for field in obj:
                obj[field] = obj[field].replace('.0', '')

            # Write the updated object to the output file
            writer.write(obj)

def on_submit():
   # Get the prompt from the input field
   prompt = input_field.get()


   # Make the completion request
   completion = openai.Completion.create(model=config.model_name, prompt=prompt, max_tokens=150)


   # Clear the input field
   input_field.delete(0, "end")


   # Get the completion text from the first choice in the choices list
   text = completion.choices[0]["text"]


   # Display the completion in the result text area
   result_text.config(state="normal")
   result_text.delete("1.0", "end")
   result_text.insert("end", text)
   result_text.config(state="disabled")


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

    #Generate prompts
    # generate_prompts(df)

    #Format prompt/completion pairs.
    # format_prompts("data/prompt_completion_pairs_prepared.jsonl", "data/prompt_completion_pairs_formatted.jsonl")

    # Create the main window
    window = tk.Tk()
    window.title("Fine-tuned GPT-3")

    # Create the input field and submit button
    input_field = tk.Entry(window)
    submit_button = tk.Button(window, text="Submit", command=on_submit)

    # Create the result text area
    result_text = tk.Text(window, state="normal", width=80, height=20)

    # Add the input field, submit button, and result text area to the window
    input_field.pack()
    submit_button.pack()
    result_text.pack()

    # Run the main loop
    window.mainloop()