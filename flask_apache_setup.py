#!/usr/bin/python3

import subprocess
import argparse
import re
import os

NUM_PATTERN = re.compile(r'^(\d+)-\w+')

WSGI_FILE = """
import sys
sys.path.insert(0, '%s')
from app import app as application
"""

APACHE_CONFIG_DIR = '/etc/apache2/sites-available/'

APACHE_CONFIG = """
<virtualhost *:80>
    ServerName %s
    ServerAlias %s.local

    WSGIDaemonProcess %s user=dlu group=dlu threads=5
    WSGIScriptAlias / %s

    <directory %s>
        WSGIProcessGroup %s
        WSGIApplicationGroup %%{GLOBAL}
        # WSGIScriptReloading On
        #Order deny,allow
        #Allow from all
        Require all granted
    </directory>
</virtualhost>
"""

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('name')
    parser.add_argument('url')
    args = parser.parse_args()

    subprocess.call(['sudo', 'apt-get', 'install', '-y', 'libapache2-mod-wsgi', 'libapache2-mod-wsgi-py3'])

    # TODO: Automatically derive name of app
    main_dir = os.path.abspath(os.path.curdir)
    wsgi_filename = os.path.join(main_dir, '%s.wsgi' % args.name)
    with open(wsgi_filename, 'w') as f:
        f.write(WSGI_FILE % main_dir)

    numbers = set()
    for filename in os.listdir(APACHE_CONFIG_DIR):
        m = NUM_PATTERN.search(filename)
        if m:
            numbers.add(m.group(1))
    c = 0
    while True:
        cs = '%03d' % c
        if cs not in numbers:
            break
        c += 1

    filename = '%03d-%s.conf' % (c, args.name)
    apache_config_path = os.path.join(APACHE_CONFIG_DIR, filename)
    with open(apache_config_path, 'w') as f:
        f.write(APACHE_CONFIG % (args.url, args.name, args.name, wsgi_filename, main_dir, args.name))

    subprocess.call(['sudo', 'a2ensite', filename])
    subprocess.call(['sudo', 'service', 'apache2', 'reload'])
