#!/usr/bin/python

import re
from collections import OrderedDict
from git import get_remotes

PATTERN = re.compile('\[([^\]]*)\]\s*(.*)$', re.DOTALL)
PATTERN2 = re.compile('(\w+)\s*=([^=]*)\s*', re.DOTALL)
PATTERN3 = re.compile('remote\.(\w+)\.url')

TEMPLATE = 'git config --get remote.%(name)s.url || git remote add %(name)s %(url)s'

HOME = '/home/dlu'

class MR:
    def __init__(self, fn=HOME + "/.mrconfig"):
        self.fn = fn
        self.repos = OrderedDict()
        sections = open(fn).read().strip().split("\n\n")
        for section in sections:
            result = PATTERN.match(section)
            if result:
                name = result.group(1)
                rest = result.group(2)
                commands = OrderedDict()
                for r2 in PATTERN2.findall(rest):
                    commands[ r2[0] ] = r2[1].strip()
                self.repos[name] = commands
                
    def check_remotes(self):
        for name, commands in self.repos.iteritems():
            checkout = commands['checkout']
            if 'git' not in checkout:
                continue
            remotes = get_remotes(HOME + '/' + name)
            if 'origin' in remotes:
                o = remotes['origin']
                if o in checkout:
                    del remotes['origin']
                else:
                    print "ERROR: Origin not the checkout command for", name
                    continue
            if len(remotes)==0:
                continue
                
            print commands
            new_remotes = []
            old_remotes = commands.get('remote', '')
            for a in PATTERN3.findall(old_remotes):
                if a in remotes:
                    del remotes[a]
            print old_remotes
            new_remotes = filter(None, map(str.strip, old_remotes.split('\n')))

            print "==%s=="%name
            print remotes
            
            for remote in remotes:
                x = raw_input(remote + "?")
                if 'a' in x:
                    print "Adding %s"%remote
                    new_remotes.append(TEMPLATE % {'name': remote, 'url': remotes[remote]})

            print new_remotes
            if len(new_remotes)>1:
                commands['remote'] = '\n    ' + '\n    '.join(new_remotes)
            elif len(new_remotes)>0:
                commands['remote'] = new_remotes[0]
              
            
    def write(self, fn=None):
        if fn is None:
            fn = self.fn
        with open(fn, 'w') as mrfile:
            for n, commands in self.repos.iteritems():
                mrfile.write('[%s]\n'%n)
                for name, command in commands.iteritems():
                    mrfile.write('%s = %s\n'%(name, command))
                mrfile.write('\n')
            


if __name__=='__main__':
    m = MR()
    m.check_remotes()
    m.write(HOME + "/.mrconfig2")

