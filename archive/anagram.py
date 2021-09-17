#!/usr/bin/python

import argparse
import collections
import copy
import itertools

ALPHABET = 'abcdefghijklmnopqrstuvwxyz'

class Counts(collections.defaultdict):
    def __init__(self, word=None):
        collections.defaultdict.__init__(self, int)
        if word is None:
            self.words = []
            self.n = 0
        else:
            self.words = [word]
            for c in word.lower():
                self[c] += 1
            self.n = len(word)

    def has_letter(self, letter, lcount):
        return self[letter] > lcount

    def subcopy(self, addons):
        cpy = Counts()
        for k,v in self.iteritems():
            cpy[k]=v
            cpy.n += v
        for k,v in addons.iteritems():
            cpy[k]-=v
            cpy.n -= v
        return cpy

    def __repr__(self):
        return ' '.join(['%s%d'%x for x in self.items() if x[1]>0])

    def __lt__(self, other):
        s1 = self.n
        s2 = other.n
        if s1 != s2:
            return s1 < s2
        for letter in sorted(set(self.keys() + other.keys())):
            a = self[letter]
            b = other[letter]
            if a != b:
                return a < b
        return None

def load_dictionary(filename):
    words = {}
    for word in open(filename, 'r').readlines():
        word = word.strip().lower()
        if len(word) == 0:
            continue
        if len(word)==1 and word not in 'ai':
            continue
        counts = Counts(word)
        key = str(counts)
        if key not in words:
            words[key] = counts
        else:
            words[key].words.append(word)
    return words.values()

class LetterTree:
    processed = 0
    total = 0
    last = None

    def __init__(self, counts=None):
        if counts is None:
            self.counts =Counts()
        else:
            self.counts = counts
        self.letter = None
        self.left = None
        self.right = None

    def split(self, queue):
        if LetterTree.total == 0:
            LetterTree.total = len(queue)

        best = 1.1
        bestL = 'a'
        for letter in ALPHABET:
            pcount = self.counts[letter]
            c = 0
            for counts in queue:
                if counts.has_letter(letter, pcount):
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
        for counts in queue:
            if counts.n == self.counts.n:
                self.counts.words += counts.words
                LetterTree.processed += 1
            elif counts.has_letter(self.letter, pcount):
                a.append(counts)
            else:
                b.append(counts)
        r = LetterTree.processed / float(LetterTree.total)
        s = '%.2f' % r
        if s != LetterTree.last:
            LetterTree.last = s
            print '%d%% Complete' % (int(100 * r))

        if len(a) > 0:
            lstate = self.counts.subcopy({self.letter: -1})
            self.left = LetterTree(lstate)
            self.left.split(a)
        if len(b) > 0:
            self.right = LetterTree(self.counts)
            self.right.split(b)

    def get_anagram_sets(self, remaining):
        anagrams = []
        if len(self.counts.words)>0:
            anagrams.append(self.counts)

        if remaining.n == 0:
            return anagrams

        if remaining[self.letter]>0 and self.left:
            c2 = remaining.subcopy({self.letter: 1})
            left_a = self.left.get_anagram_sets(c2)
            anagrams += left_a

        if self.right:
            right_a = self.right.get_anagram_sets(remaining)
            anagrams += right_a

        return anagrams


def get_anagrams(base_count, root):
    node = root
    state = collections.defaultdict(int)
    while node:
        if node.counts.n == base_count.n:
            return node.counts.words
        elif base_count.has_letter(node.letter, state[node.letter]):
            state[node.letter] += 1
            node = node.left
        else:
            node = node.right
    return []

class AnagramTree:
    def __init__(self, parent=None, counts=None):
        self.counts = counts
        self.children = []
        self.parent = parent

    def valid_count(self, count):
        if self.parent is None:
            return True
        if self.counts < count:
            return False
        return self.parent.valid_count(count)

    def __repr__(self, depth=0):
        s = ' ' * depth
        if self.parent is None:
            inc = 0
        else:
            s += str(self.counts.words)
            s += '\n'
            inc = 1
        for child in sorted(self.children, key=lambda d: d.counts):
            s += child.__repr__(depth+inc)
        return s

    def get_multiword_anagram(self, count, root, depth=0):
        anagrams = root.get_anagram_sets(count)
        for i, count_x in enumerate(anagrams):
            if not self.valid_count(count_x):
                continue
            if depth==0:
                print ' '*depth + '%d/%d'%(i,len(anagrams))
            child = AnagramTree(parent=self, counts=count_x)
            c2 = count.subcopy(count_x)
            res = child.get_multiword_anagram(c2, root, depth=depth+1)
            if res:
                self.children.append(res)
        if sum(count.values())>0 and len(self.children)==0:
            return None
        return self

    def flatten(self, parents=None):
        if parents is None:
            if self.counts:
                parents = [self.counts]
            else:
                parents = []
        else:
            parents = parents + [self.counts]
        results = []
        if len(self.children)==0:
            results.append(parents)
        else:
            for child in self.children:
                if child is None:
                    continue
                results += child.flatten(parents)

        return results

def get_multiword_anagram(counts, root):
    node = AnagramTree()
    node.get_multiword_anagram(counts, root)
    return node

def all_variations(tree):
    results = []
    for row in tree.flatten():
        sub = []
        for count in row:
            if len(sub)==0:
                sub = count.words
            else:
                sub = list(itertools.product(sub, count.words))
        results += sub
    return results

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('basis', nargs='+')
    parser.add_argument('-d', '--dictionary', default='/etc/dictionaries-common/words')
    parser.add_argument('-s', '--single', action='store_true')
    parser.add_argument('-ss', '--sub', action='store_true')
    parser.add_argument('-m', '--multi', action='store_true')
    args = parser.parse_args()

    basis = ''.join(args.basis)
    base_count = Counts(basis)
    print basis, base_count

    dictionary = load_dictionary(args.dictionary)

    print 'Dictionary Loaded'
    root = LetterTree()
    root.split(dictionary)
    print 'Dictionary Processed'

    if args.single:
        print get_anagrams(base_count, root)
    if args.sub:
        sets = root.get_anagram_sets(base_count)
        for counts in sorted(sets):
            print counts.words

    if args.multi:
        tree = get_multiword_anagram(base_count, root)
        for x in sorted(all_variations(tree), key=lambda d: sum([pow(len(x),2) for x in d])):
            print x
