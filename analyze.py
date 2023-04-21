#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

#Link to dataset
# https://www.kaggle.com/datasets/ulrikthygepedersen/airlines-delay

def format_dataset(df):
    """
    Function to format the airlines.csv dataset.
    :param df: pandas dataframe
    :return: formatted pandas dataframe
    """
    #Drop columns not relevant for project

    #Renaming Delay
    df['Delay'] = df['Class'].map({0: 'no', 1: 'yes'})
    df = df.drop(['Class'], axis=1)
    #Renaming DayOfWEek and ordering
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    df['DayOfWeek'] = pd.Categorical(df['DayOfWeek'].map({1: 'Mon', 2: 'Tue', 3:'Wed', 4:'Thu', 5:'Fri', 6:'Sat', 7:'Sun'}), days)
    #Departure time in hours (am/pm) and rename row
    df['Time'] = (df['Time']/60).round(2)
    df["DepartureTime"] = df["Time"]
    df = df.drop(["Time"], axis=1)

    return df

if __name__ == '__main__':
    flight_data = pd.read_csv("data/airlines_delay.csv")

    #Colum names
    print(flight_data.columns)
    print(flight_data.shape)
    #Numer of airlines
    print(flight_data["Airline"].nunique())
    print(flight_data["Length"].iloc[0:5])
    #Formating dataset
    flight_data = format_dataset(flight_data)

    #Show number of delayed flights
    # plt.title("Number of delayed flights")
    # fig = sns.countplot(x=flight_data["Delay"])
    # fig.set(xlabel='Delay', ylabel='Number of flights')
    #
    # plt.show()

    #Delayed flights by company
    # sns.set_style("whitegrid")
    # chart = sns.catplot(data=flight_data, x="Airline", kind="count")
    # chart.fig.subplots_adjust(top=.95)
    # chart.set_axis_labels("Airlines", "Number of Delays")
    # chart.ax.set_title("Delays by airline")
    #
    # plt.show()

    #Delayed flights by airport
    # Ocurrences of airports. There are too many airport to visualize.

    #Delayed flights by length

    #Delayed flights by weekday
    # sns.set_style("whitegrid")
    # chart = sns.histplot(data=flight_data, x="DayOfWeek", hue="Delay", multiple="stack", discrete=True)
    # for bars in chart.containers:
    #     heights = [b.get_height() for b in bars]
    #     labels = [f'{h:1f}%' if h > 0.001 else '' for h in
    #               heights]
    #     chart.bar_label(bars, labels=labels, label_type='center')
    # chart.yaxis.set_major_formatter(PercentFormatter(1))

    #This is the same as the code above. Something is wrong with % formatting.
    # for p in chart.patches:
    #     txt = str(int(p.get_height())) + '%'
    #     txt_x = p.get_x()
    #     txt_y = p.get_height()
    #     chart.text(txt_x, txt_y, txt)

    # Show the plot
    # plt.show()

    # chart.fig.subplots_adjust(top=.95)
    # chart.set_axis_labels("Day of Week", "Number of Delays")
    # chart.ax.set_title("Flights by weekday")

    # plt.show()