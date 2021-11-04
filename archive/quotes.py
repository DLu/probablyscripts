import random


def get_random_quote():
    f = open('/home/dlu/Projects/probablyscripts/quotes.txt', 'r')
    lines = f.readlines()
    chosen = random.choice(lines)
    return [s.strip() for s in chosen.split('-')]
