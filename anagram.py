#!/usr/bin/python

import sys
import collections
import copy

ALPHABET = 'abcdefghijklmnopqrstuvwxyz'


def has_letter(letter, counts, pcount):
    return counts[letter] > pcount


def to_counts(s):
    counts = collections.defaultdict(int)
    for c in s.lower():
        if c not in ALPHABET:
            return None
        counts[c] += 1
    return counts


class Node:
    processed = 0
    total = 0
    last = None

    def __init__(self, state=collections.defaultdict(int)):
        self.words = []
        self.letter = None
        self.left = None
        self.right = None
        self.state = state
        self.N = 0

    def split(self, queue):
        if Node.total == 0:
            Node.total = len(queue)

        best = 1.1
        bestL = 'a'
        for letter in ALPHABET:
            pcount = self.state[letter]
            c = 0
            for word, counts in queue:
                if has_letter(letter, counts, pcount):
                    c += 1
            if c == 0:
                continue
            r = c / float(len(queue))
            # print letter, r
            if abs(r - .50) < best:
                best = abs(r - .5)
                bestL = letter

        self.letter = bestL
        self.N = sum(self.state.values())
        pcount = self.state[self.letter]
        a = []
        b = []
        for word, counts in queue:
            if len(word) == self.N:
                self.words.append(word)
            elif has_letter(self.letter, counts, pcount):
                a.append((word, counts))
            else:
                b.append((word, counts))
        # print "***********" , len(a), len(b), len(self.words)
        Node.processed += len(self.words)
        r = Node.processed / float(Node.total)
        s = '%.2f' % r
        if s != Node.last:
            Node.last = s
            print '%d%% Complete' % (int(100 * r))
        # print Node.processed / float(Node.total)
        if len(a) > 0:
            lstate = copy.copy(self.state)
            lstate[self.letter] += 1
            self.left = Node(lstate)
            self.left.split(a)
        if len(b) > 0:
            self.right = Node(self.state)
            self.right.split(b)
        # print "X"

    def get_anagrams(self, counts, state=collections.defaultdict(int), n=None):
        if n is None:
            n = sum(counts.values())
        if n == self.N:
            return self.words
        elif has_letter(self.letter, counts, state[self.letter]):
            state[self.letter] += 1
            if self.left:
                return self.left.get_anagrams(counts, state, n)
        elif self.right:
            return self.right.get_anagrams(counts, state, n)
        return []
words = []

for word in open(sys.argv[1], 'r').readlines():
    word = word.strip()
    if len(word) == 0:
        continue
    letters = True
    counts = to_counts(word)
    if counts is not None:
        words.append((word, counts))


root = Node()
root.split(words)

print root.get_anagrams(to_counts(sys.argv[2]))
