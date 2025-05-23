

def filter_data(data, function):
    return data.replace(function, '')


print(filter_data('start+1234,5678', 'start+').split(','))
