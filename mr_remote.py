#!/usr/bin/python

import re

PATTERN = re.compile('\[([^\]]*)\]\s*(.*)$', re.DOTALL)
PATTERN2 = re.compile('(\w+)\s*=(.*)\s*')

class MR:
    def __init__(self, fn="/home/dlu/.mrconfig"):
        self.repos = []
        sections = open(fn).read().strip().split("\n\n")
        for section in sections:
            result = PATTERN.match(section)
            if result:
                name = result.group(1)
                rest = result.group(2)
                commands = []
                for r2 in PATTERN2.findall(rest):
                    commands.append( (r2[0], r2[1].strip() ) )
                self.repos.append( (name, commands) )
            
    def write(self, fn="/home/dlu/.mrconfig2"):
        with open(fn, 'w') as mrfile:
            for n, commands in self.repos:
                mrfile.write('[%s]\n'%n)
                for name, command in commands:
                    mrfile.write('%s = %s\n'%(name, command))
                mrfile.write('\n')
            


if __name__=='__main__':
    m = MR()
    m.write()
        
