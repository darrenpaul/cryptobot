def get_only_key_values(data, key):
    values = []
    for i in data:
        values.append(float(i['last']))
    return values
