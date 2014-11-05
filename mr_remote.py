#!/usr/bin/python

import re
from collections import OrderedDict
from git import get_remotes

PATTERN = re.compile('\[([^\]]*)\]\s*(.*)$', re.DOTALL)
PATTERN3 = re.compile('.*remote\.(\w+)\.url.*')

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
                cn = None
                cc = []
                for line in rest.split('\n'):
                    line = line.strip()
                    if '=' in line:
                        if cn is not None:
                            commands[cn] = cc
                        cn, _, l2 = line.partition('=')
                        cn = cn.strip()
                        l2=l2.strip()
                        if len(l2)>0:
                            cc = [l2.strip()]
                        else:
                            cc = []
                    else:
                        if len(line)>0:
                            cc.append(line)
                if cn is not None:
                    commands[cn] = cc

                self.repos[name] = commands
                
    def check_remotes(self):
        for name, commands in self.repos.iteritems():
            checkout = commands['checkout'][0]
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
                
            new_remotes = []
            old_remotes = commands.get('remote', [])
            for line in old_remotes:
                a = PATTERN3.match(line)
                if a and a.group(1) in remotes:
                    del remotes[a.group(1)]
            new_remotes = old_remotes
            
            if len(remotes)==0:
                continue

            print "==%s=="%name
            print remotes
            
            for remote in remotes:
                x = raw_input(remote + "?")
                if 'a' in x:
                    print "Adding %s"%remote
                    new_remotes.append(TEMPLATE % {'name': remote, 'url': remotes[remote]})

            commands['remote'] = new_remotes
              
            
    def write(self, fn=None):
        if fn is None:
            fn = self.fn
        with open(fn, 'w') as mrfile:
            for n, commands in self.repos.iteritems():
                mrfile.write('[%s]\n'%n)
                for name, command_list in commands.iteritems():
                    if len(command_list)==1:
                        mrfile.write('%s = %s\n'%(name, command_list[0]))
                    else:
                        mrfile.write('%s = \n    ' %name + '\n    '.join(command_list))
                        mrfile.write('\n')
                mrfile.write('\n')
            


if __name__=='__main__':
    m = MR()
    m.check_remotes()
    m.write(HOME + "/.mrconfig2")

