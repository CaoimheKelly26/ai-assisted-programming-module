"""
Messy Code - Refactor me!

This code works but is poorly written. Use Copilot Edit mode to refactor it.

Instructions:
1. Select all the code
2. Press Ctrl+I / Cmd+I
3. Ask Copilot to refactor following best practices
4. Compare before and after
"""
import json


def _sum_and_extremes(numbers):
    total = 0
    maximum = 0
    minimum = 0
    for number in numbers:
        total += number
        if number > maximum:
            maximum = number
        if minimum == 0:
            minimum = number
        elif number < minimum:
            minimum = number
    return total, maximum, minimum


def calc(numbers):
    total, maximum, minimum = _sum_and_extremes(numbers)
    average = total / len(numbers)
    return {'avg': average, 'max': maximum, 'min': minimum, 'sum': total}


def _process_active_item(item):
    value = item['value']
    return {
        'id': item['id'],
        'value': value * 1.1,
        'priority': 'high' if value > 100 else 'low',
    }


def proc_data(data):
    return [
        _process_active_item(item)
        for item in data
        if item['status'] == 'active'
    ]


def get_stuff(filename):
    with open(filename, 'r') as input_file:
        data = json.load(input_file)

    active = [item for item in data if item['status'] == 'active']
    inactive = [item for item in data if item['status'] != 'active']
    return active, inactive


# Test code
if __name__ == '__main__':
    numbers = [10, 20, 30, 40, 50]
    result = calc(numbers)
    print(result)

    data = [
        {'id': 1, 'status': 'active', 'value': 150},
        {'id': 2, 'status': 'active', 'value': 80},
        {'id': 3, 'status': 'inactive', 'value': 200},
    ]

    processed = proc_data(data)
    print(processed)
