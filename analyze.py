#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


if __name__ == '__main__':
    flight_data = pd.read_csv("airlines.csv")
    flight_data['Delay'] = flight_data['Delay'].map({0: 'no', 1: 'yes'})

    #Show number of delayed flights
    # plt.title("Number of delayed flights")
    # fig = sns.countplot(x=flight_data["Delay"])
    # fig.set(xlabel='Delay', ylabel='Number of flights')
    #
    # plt.show()

    #Delayed flights by company

    #Delayed flights by airport

    #Delayed flights by length

    #Delayed flights by weekday

