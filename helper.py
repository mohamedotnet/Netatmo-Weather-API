from itertools import chain

""" 
    Average : Sum all the values stored - since scale = 'max' - and divide it by how many values are stored
    Minimum : Get the local minimum (from every record), then the global minimum
    Maximum: Get the local maximum (from every record), then the global maximum

"""
def get_min_max_avg_temperature(temperatures):
    local_mins = []
    local_max = []
    number_of_values = 0
    sum_of_values = 0

    for temperature in temperatures:
        local_values = list(chain.from_iterable(temperature['value']))

        number_of_values += len(local_values)
        sum_of_values += sum(local_values)

        local_mins.append(min(local_values))
        local_max.append(max(local_values))

    
    return min(local_mins), max(local_max), float("% 0.2f" % (sum_of_values/number_of_values))

