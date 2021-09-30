#!/usr/bin/python3
import argparse

import pyphen

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()

    dic = pyphen.Pyphen(lang='en')

    for line in open(args.filename):
        syllables = []
        for word in line.split():
            w_syllables = dic.inserted(word).split('-')
            syllables += [f'{s}-' for s in w_syllables[:-1]]
            syllables.append(w_syllables[-1])
        print('\t'.join(syllables))
