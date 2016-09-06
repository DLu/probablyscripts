#!/usr/bin/python

import argparse
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
        self.word_length = 0

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
            if abs(r - .50) < best:
                best = abs(r - .5)
                bestL = letter

        self.letter = bestL
        self.word_length = sum(self.state.values())
        pcount = self.state[self.letter]
        a = []
        b = []
        for word, counts in queue:
            if len(word) == self.word_length:
                self.words.append(word)
            elif has_letter(self.letter, counts, pcount):
                a.append((word, counts))
            else:
                b.append((word, counts))

        Node.processed += len(self.words)
        r = Node.processed / float(Node.total)
        s = '%.2f' % r
        if s != Node.last:
            Node.last = s
            print '%d%% Complete' % (int(100 * r))
        
        if len(a) > 0:
            lstate = copy.copy(self.state)
            lstate[self.letter] += 1
            self.left = Node(lstate)
            self.left.split(a)
        if len(b) > 0:
            self.right = Node(self.state)
            self.right.split(b)

    def get_anagrams(self, counts, state=collections.defaultdict(int), n=None):
        if n is None:
            n = sum(counts.values())
        if n == self.word_length:
            return self.words
        elif has_letter(self.letter, counts, state[self.letter]):
            state[self.letter] += 1
            if self.left:
                return self.left.get_anagrams(counts, state, n)
        elif self.right:
            return self.right.get_anagrams(counts, state, n)
        return []
        
    def get_anagram_sets(self, counts):
        remaining_letters = sum(counts.values())
        if remaining_letters == 0:
            return []
        if len(self.words)==0:
            if counts[self.letter]>0:
                c2 = dict(counts)
                c2[self.letter]-=1
                if self.left:
                    return self.left.get_anagram_sets(c2)
            elif self.right:
                return self.right.get_anagram_sets(counts)
        else:
            
                

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('basis', nargs='+')
    parser.add_argument('-d', '--dictionary', default='/etc/dictionaries-common/words')
    
    args = parser.parse_args()
    
    words = []

    for word in open(args.dictionary, 'r').readlines():
        word = word.strip()
        if len(word) == 0:
            continue
        counts = to_counts(word)
        if counts is not None:
            words.append((word.lower(), counts))
    print 'Dictionary Loaded'

    root = Node()
    root.split(words)
    print 'Dictionary Processed'

    print root.get_anagrams(to_counts(' '.join(args.basis)))
