#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import PercentFormatter

if __name__ == '__main__':
    flight_data = pd.read_csv("airlines.csv")
    #Renaming Delay
    flight_data['Delay'] = flight_data['Delay'].map({0: 'no', 1: 'yes'})
    #Renaming DayOfWEek and ordering
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    flight_data['DayOfWeek'] = pd.Categorical(flight_data['DayOfWeek'].map({1: 'Mon', 2: 'Tue', 3:'Wed', 4:'Thu', 5:'Fri', 6:'Sat', 7:'Sun'}), days)
    #Colum names
    # print(flight_data.columns)
    #Numer of airlines
    # print(flight_data["Airline"].nunique())

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
    sns.set_style("whitegrid")
    chart = sns.histplot(data=flight_data, x="DayOfWeek", hue="Delay", multiple="stack", discrete=True)
    for bars in chart.containers:
        heights = [b.get_height() for b in bars]
        labels = [f'{h:.1f}%' if h > 0.001 else '' for h in
                  heights]
        chart.bar_label(bars, labels=labels, label_type='center')
    # chart.yaxis.set_major_formatter(PercentFormatter(1))

    # chart.fig.subplots_adjust(top=.95)
    # chart.set_axis_labels("Day of Week", "Number of Delays")
    # chart.ax.set_title("Flights by weekday")

    plt.show()