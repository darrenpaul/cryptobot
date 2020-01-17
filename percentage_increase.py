def get_percentage_increase(value, percentage):
    value = float(value)
    percentage = float(percentage)
    percentage_of = value/percentage
    return value + percentage_of
