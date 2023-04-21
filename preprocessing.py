#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

import pandas as pd
import tiktoken

def convert_to_time(num):
    """
    Converts a number in the format `hour.minute` to a string in the format `hour:minute`.

    :param num: A float representing the time in hours and minutes, e.g. 6.00, 19.30.
    :return: A string in the format `hour:minute`, e.g. "06:00", "19:30".
    :rtype: str
    """
    hours = int(num)
    minutes = int((num - hours) * 60)
    return f"{hours:02d}:{minutes:02d}"
def format_dataset(df):
    """
    Function to format the airlines.csv dataset.
    :param df: pandas dataframe
    :return: formatted pandas dataframe
    """

    #Renaming Delay
    df['Delay'] = df['Class'].map({0: 'no', 1: 'yes'})
    df = df.drop(['Class'], axis=1)
    #Renaming DayOfWEek and ordering
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    df['DayOfWeek'] = pd.Categorical(df['DayOfWeek'].map({1: 'Mon', 2: 'Tue', 3:'Wed', 4:'Thu', 5:'Fri', 6:'Sat', 7:'Sun'}), days)
    #Departure time in hours (am/pm) and rename row
    df['Time'] = (df['Time']/60).round(2)
    df["DepartureTime"] = df["Time"]
    df["DepartureTime"] = df["DepartureTime"].apply(lambda x: convert_to_time(x))
    df = df.drop(["Time"], axis=1)
    #Change datatype of columns to remove zeros.
    df["Flight"], df["Length"] = df["Flight"].astype(int), df["Length"].astype(int)

    return df

def write_random_rows_to_csv(df, filename: str, nrows: int=1000):
    """
    Writes 1000 random rows from a pandas DataFrame to a CSV file.

    Parameters:
    df (pandas DataFrame): The DataFrame to select random rows from.
    filename (str): The name of the CSV file to write the random rows to.
    :param df: The DataFrame to select random rows from.
    :param filename: The name of the CSV file to write the random rows to.
    :param nrows: The number of rows.
    :return: None
    """
    # Select 1000 random rows
    random_rows = df.sample(n=nrows)

    # Write the random rows to a CSV file
    random_rows.to_csv(filename, index=False)

def generate_prompts(df):
    """
    Function to generate completion prompts from df for fine-tuning LLM.
    :param df: pandas dataframe with airline data
    :return:
    """
    # Iterate through each row in the dataframe and create a prompt and completion pair
    prompt_completion_pairs = []
    for index, row in df.iterrows():
        prompt = f"Provide a written summary of Flight {row['Flight']}, operated by {row['Airline']}, which departed from {row['AirportFrom']} to {row['AirportTo']} on {row['DayOfWeek']} at {row['DepartureTime']} hours and had a flight length of {row['Length']} minutes."
        completion = f"Flight {row['Flight']} operated by {row['Airline']} departed from {row['AirportFrom']} to {row['AirportTo']} on {row['DayOfWeek']} at {row['DepartureTime']} hours and had a flight length of {row['Length']} minutes. The delay status was {row['Delay']}."
        prompt_completion_pairs.append(
            {"prompt": prompt, "completion": completion})

    # Export the prompt and completion pairs to a JSON file
    with open("data/test.jsonl", "w") as outfile:
        json.dump(prompt_completion_pairs, outfile)

def num_tokens_from_string(string: str, encoding="cl100k_base") -> int:
    """
    Function to count the number of tokens in a string using tiktoken
    :param string:
    :param encoding_name: name of tiktoken encoding
    :return:
    """
    encoding = tiktoken.get_encoding(encoding)
    num_tokens = len(encoding.encode(string))
    return num_tokens

if __name__ == '__main__':
    df = pd.read_csv("data/airlines_delay.csv")
    df = format_dataset(df)
    #Generate completion pairs and write to file.
    generate_prompts(df)

    #Generate small dataset for direct input to LLM prompt.
    write_random_rows_to_csv(df, "data/airlines_delay_small.csv")
