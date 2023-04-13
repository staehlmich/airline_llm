#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import openai
import config
import pandas as pd

openai.api_key = config.OPENAI_API_KEY


if __name__ == '__main__':

    #TODO: How to create github repo from PyCharm?
    prompt = "Is flight 1558 delayed?"
    # resp = openai.Completion.create(model="text-davinci-003", prompt=prompt,
  # temperature=0)
    # print(resp["choices"][0]['text'])

    # Response without fine-tuning:
    #"\n\nIt is not possible to answer this question without more information."

    # df = pd.read_csv("Airlines.csv")
    # print(df.columns)
    # print(df.iloc[1])