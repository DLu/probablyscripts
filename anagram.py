#!/usr/bin/python

import argparse
import collections
import copy

ALPHABET = 'abcdefghijklmnopqrstuvwxyz'

def count_cmp(c1, c2):
    s1 = sum(c1.values())
    s2 = sum(c2.values())
    if s1 != s2:
        #print count_str(c1), ';', count_str(c2), ';', s1, s2, s1<s2
        return s1 < s2
    for letter in sorted(set(c1.keys() + c2.keys())):
        a = c1[letter]
        b = c2[letter]
        if a != b:
            #print count_str(c1), '|', count_str(c2), '|', letter, a, b, a<b
            return a < b
    return None


class LetterSet:
    def __init__(self, counts, words=None):
        self.counts = counts
        if words is None:
            self.words = []
        else:
            self.words = words
        self.letter_count = sum(counts.values())

    def __lt__(self, other):
        if self.letter_count != other.letter_count:
            return self.letter_count < other.letter_count
        for letter in set(self.counts.keys() + other.counts.keys()):
            a = self.counts[letter]
            b = other.counts[letter]
            if a != b:
                return a < b
        return None

class AnagramTree:
    def __init__(self, parent=None, words=None):
        if words is None:
            self.words = []
        else:
            self.words = words
        self.children = []
        self.parent = parent

    def valid_count(self, count):
        if self.parent is None:
            return True
        c = to_counts(self.words[0])
        if not count_cmp(count, c):
            return False
        return self.parent.valid_count(count)

    def __repr__(self, depth=0):
        s = ' ' * depth
        if self.parent is None:
            inc = 0
        else:
            s += str(self.words)
            s += '\n'
            inc = 1
        for child in sorted(self.children, key=lambda d: -len(d.words[0])):
            s += child.__repr__(depth+inc)
        return s

def has_letter(letter, counts, pcount):
    return counts[letter] > pcount

def to_counts(s):
    counts = collections.defaultdict(int)
    for c in s.lower():
        if c not in ALPHABET:
            return None
        counts[c] += 1
    return counts

def count_str(counts):
    return ' '.join(['%s%d'%x for x in counts.items() if x[1]>0])

class Node(LetterSet):
    processed = 0
    total = 0
    last = None

    def __init__(self, state=collections.defaultdict(int)):
        LetterSet.__init__(self, state)
        self.letter = None
        self.left = None
        self.right = None

    def split(self, queue):
        if Node.total == 0:
            Node.total = len(queue)

        best = 1.1
        bestL = 'a'
        for letter in ALPHABET:
            pcount = self.counts[letter]
            c = 0
            for word, counts in queue:
                if has_letter(letter, counts, pcount):
                    c += 1
            if c == 0:
                continue
            r = c / float(len(queue))
            if False and r==1.0:
                bestL = letter
                break
            elif abs(r - .50) < best:
                best = abs(r - .5)
                bestL = letter
        self.letter = bestL
        pcount = self.counts[self.letter]
        a = []
        b = []
        for word, counts in queue:
            if len(word) == self.letter_count:
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
            lstate = copy.copy(self.counts)
            lstate[self.letter] += 1
            self.left = Node(lstate)
            self.left.split(a)
        if len(b) > 0:
            self.right = Node(self.counts)
            self.right.split(b)

    def get_anagrams(self, counts, state=collections.defaultdict(int), n=None):
        if n is None:
            n = sum(counts.values())
        if n == self.letter_count:
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
            if len(self.words)>0:
                return [self.words]
            else:
                return []
        anagrams = []
        if len(self.words)>0:
            anagrams.append(self.words)
        if counts[self.letter]>0 and self.left:
            c2 = copy.copy(counts)
            c2[self.letter]-=1
            left_a = self.left.get_anagram_sets(c2)
            if len(left_a)>0:
                anagrams.extend(left_a)
        if self.right:
            right_a = self.right.get_anagram_sets(counts)
            if len(right_a)>0:
                anagrams.extend(right_a)
        return anagrams

    def get_multiword_anagram(self, counts, node=None, depth=0):
        if node is None:
            node = AnagramTree()
        anagrams = self.get_anagram_sets(counts)
        for i, words in enumerate(anagrams):
            if depth<=0:
                print ' '*depth + '%d/%d'%(i,len(anagrams))
            child = AnagramTree(parent=node, words=words)
            word = words[0]
            pc = to_counts(word)
            c2 = copy.copy(counts)
            for l,c in pc.iteritems():
                c2[l] -= c
            valid = node.valid_count(pc)
            if not valid:
                continue
            res = self.get_multiword_anagram(c2, child, depth=depth+1)
            if res:
                node.children.append(res)
        if sum(counts.values())>0 and len(node.children)==0:
            return None
        return node

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('basis', nargs='+')
    parser.add_argument('-d', '--dictionary', default='/etc/dictionaries-common/words')
    parser.add_argument('-s', '--single', action='store_true')
    parser.add_argument('-ss', '--sub', action='store_true')
    parser.add_argument('-m', '--multi', action='store_true')
    args = parser.parse_args()

    words = []

    for word in open(args.dictionary, 'r').readlines():
        word = word.strip()
        if len(word) == 0:
            continue
        if len(word)==1 and word not in 'ai':
            continue
        counts = to_counts(word)
        if counts is not None:
            words.append((word.lower(), counts))
    print 'Dictionary Loaded'
    root = Node()
    root.split(words)
    print 'Dictionary Processed'

    counts = to_counts(' '.join(args.basis))
    if args.single:
        print root.get_anagrams(counts)
    if args.sub:
        print root.get_anagram_sets(counts)

    if args.multi:
        tree = root.get_multiword_anagram(counts)
        print tree
