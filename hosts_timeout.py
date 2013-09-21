#!/usr/bin/python

#HOSTS = '/etc/hosts'
HOSTS = 'hosts'

def read_hosts():
    return open(HOSTS, 'r').readlines()


def write_hosts(lines):
    f = open(HOSTS, 'w')
    for line in lines:
        f.write(line)
    f.close()

def toggle(lines, domain):
    newlines = []

    for line in lines:
        if '\t' not in line:
            newlines.append(line)
            continue
            
        ip, domains = line.split('\t')
        if domain in domains:
            if ip[0]=='#':
                newlines.append( line[1:] )
            else:
                newlines.append( '#' + line )
        else:
            newlines.append(line)

    return newlines
    
lines = read_hosts()
lines = toggle(lines, 'facebook.com')
write_hosts(lines)                

