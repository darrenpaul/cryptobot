import pandas
import numpy


def get_max(data=None):
    if data and isinstance(data, list):
        df = pandas.DataFrame(data=data)
        return float(df.max().item())


def get_min(data=None):
    if data and isinstance(data, list):
        df = pandas.DataFrame(data=data)
        return float(df.min().item())


def get_mean(data=None):
    if data and isinstance(data, list):
        float_values = []
        for value in data:
            float_values.append(float(value))
        df = pandas.DataFrame(data=float_values)
        return float(df.mean().item())


def get_weighted_average(data, key_one, key_two):
    total_value_one = 0.0
    total_value_two = 0.0

    for i in data:
        value_one = float(i[key_one])
        value_two = float(i[key_two])

        total_value_one += value_one * value_two
        total_value_two += value_two

    return total_value_one / total_value_two


def get_median(data=None):
    if data and isinstance(data, list):
        df = pandas.DataFrame(data=data)
        return float(df.median().item())


def get_standard_deviation(data=None):
    if data and isinstance(data, list):
        df = pandas.DataFrame(data=data)
        std = float(df.std().item())
        if pandas.isna(std):
            std = 0.0
        return float(std)


def get_percentage(value=None, percentage=25):
    return float(float(value) * float(percentage) / 100)


def get_percentage_difference(value1=None, value2=None):
    difference = get_difference(value1=value1, value2=value2)
    average = float(value1) + float(value2) / 2
    return (difference / average) * 100


def get_difference(value1=None, value2=None):
    return float(value1) - float(value2)


def calculate_simple_moving_average(values=None, period=5):
    float_values = []
    for value in values:
        float_values.append(float(value))
    return float(get_mean(float_values[period - 1 :]))


def get_variance(data=None):
    std = get_standard_deviation(data=data)
    mean = get_mean(data=data)

    high = float(mean + std)
    low = float(mean - std)

    return {"std": std, "mean": mean, "high": high, "low": low}


def get_trend(data, size=6):
    if len(data) < size:
        return 0

    portion = int(size / 2)

    usable_data = data[-size:]
    initial = get_mean(usable_data[:portion])
    final = get_mean(usable_data[portion:])

    if initial == 0.0 or final == 0.0:
        return 100

    return (final / initial) * 100


def round_down(value, decimals=2):
    return float(numpy.floor(float(value) * (10**decimals)) / (10**decimals))


def round_up(value, decimals=2):
    return float(numpy.ceil(float(value) * (10**decimals)) / (10**decimals))
