import numpy
import pandas


def get_percentage_increase(value, percentage):
    value = float(value)
    percentage = float(percentage)
    percentage_of = value/percentage
    return value + percentage_of


def get_mean(data):
    df = pandas.DataFrame(data=data)
    return float(df.mean())
