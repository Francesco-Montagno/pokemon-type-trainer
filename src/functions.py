import random

from data.type_chart import TYPE_CHART

def generate_random_values():
    type_1 = random.randint(0,17)
    type_2 = random.randint(0,17)
    return type_1, type_2

def generate_question(type_1, type_2):
    return TYPE_CHART[type_1][type_2]
