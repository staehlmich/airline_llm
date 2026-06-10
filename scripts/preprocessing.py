#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import os

def convert_time(minutes_since_midnight: int):
    """
    Convert time from minutes since midnight to human-readable format.
    :param minutes_since_midnight: Total minutes since midnight (e.g., 610.0 = 10:10 AM)
    :return: String in HH:MM format (24-hour)
    """
    total_minutes = int(minutes_since_midnight)
    hours = total_minutes // 60
    minutes = total_minutes % 60

    return f"{hours:02d}:{minutes:02d}"

def create_balanced_test_sample(df, nrows=100):
    """
    Function to create a class-balanced sample dataset.
    :param df: pandas dataframe in the format of airlines_delay.csv
    :param nrows: Total number of rows of sampled dataset.
    :return: sampled dataframe
    """

    # Filter and sample for Class 0 (On Time)
    on_time_df = df[df["Class"] == 0].sample(n=nrows//2, random_state=42)

    # Filter and sample for Class 1 (Delayed)
    delayed_df = df[df["Class"] == 1].sample(n=nrows//2, random_state=42)

    # Combine the two halves back together
    balanced_sample_df = pd.concat([on_time_df, delayed_df], axis=0)

    # 6. Shuffle the combined dataset so they aren't perfectly split in order
    balanced_sample_df = balanced_sample_df.sample(frac=1, random_state=42).reset_index(
        drop=True
    )

    return balanced_sample_df

def format_dataset(df):
    """
    Function to format the airlines.csv dataset.
    :param df: pandas dataframe
    :return: formatted pandas dataframe
    """

    #Renaming Delay
    df['Delay'] = df['Class'].map({0: 'no', 1: 'yes'})
    df = df.drop(['Class'], axis=1)

    #Renaming DayOfWeek and ordering
    day_map = dict(enumerate(('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'), start=1))
    df['DayOfWeek'] = pd.Categorical(df['DayOfWeek'].map(day_map), categories=day_map.values(), ordered=True)

    #Departure time in hours (am/pm) and rename row
    df = df.rename(columns={"Time": "DepartureTime"})
    df["DepartureTime"] = df["DepartureTime"].apply(lambda x: convert_time(x))

    #Apply convert_time to Length to get hour:minute format.
    df["Length"] = df["Length"].apply(lambda x: convert_time(x))

    return df


def main():
    df = pd.read_csv("data/airlines_delay.csv")

    df_sample = create_balanced_test_sample(df)

    df_formatted = format_dataset(df_sample)


    df_formatted.to_csv("data/airlines_delay_sample.csv", index=False)


if __name__ == "__main__":
    main()