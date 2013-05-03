#!/usr/bin/python

class ChainNode:
    def __init__(self, word, id, prev=None, next=None):
        self.word = word
        self.id = id
        self.prev = prev
        self.next = next

    def __repr__(self):
        return self.word

    def getFirst(self):
        node = self
        while node.prev != None:
            node = node.prev
        return node

    def wholeChain(self):
        s = ''
        x = self
        while x:
            s += x.word
            s += ' '
            x = x.next
        return s

    def length(self):
        N = 0
        x = self
        while x:
            N+=1
            x = x.next
        return N

    def reverse(self):
        current = self
        last = self
        while current:
            temp = current.prev
            current.prev = current.next
            current.next = temp
            last = current
            current = current.prev
        return last

class Subchain
