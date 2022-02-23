def get_dict_value_total(data, key):
    total = 0.0
    for i in data:
        if(key not in i):
            continue
        total += float(i.get(key))
    return total


def get_list_of_dict_values(data, key):
    values = []
    for i in data:
        if(key not in i):
            continue
        values.append(i.get(key))
    return values


def increment_value_in_dict(data, key, increment):
    for i in data:
        if key not in i:
            continue
        i[key] = float(i[key]) + float(increment)
    return data


def run_function_on_list_items(data, key, function):
    updated_data = []
    for i in data:
        updated_data.append({**i, **function(i.get(key))})
    return updated_data


def add_key_to_dict(data, key, value):
    for i in data:
        i[key] = value
    return data


def get_list_of_dict_when_condition_true(data, key, condition):
    values = []
    for i in data:
        if i.get(key) == condition:
            values.append(i)
    return values


def get_list_of_dict_when_condition_false(data, key, condition):
    values = []
    for i in data:
        if i.get(key) != condition:
            values.append(i)
    return values


def get_list_of_dict_when_condition_greater(data, key, condition):
    values = []
    for i in data:
        if float(i.get(key)) > condition:
            values.append(i)
    return values


def get_list_of_dict_when_condition_less(data, key, condition):
    values = []
    for i in data:
        if float(i.get(key)) < condition:
            values.append(i)
    return values