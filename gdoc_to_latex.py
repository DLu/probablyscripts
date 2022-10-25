#!/usr/bin/python3
import argparse
import pathlib
import zipfile

from bs4 import BeautifulSoup
import bs4
import cssutils


def translate(element):
    s = ''
    for child in element.children:
        if isinstance(child, bs4.element.Tag):
            tags = []

            for c_name in child.get('class', []):
                if c_name in css_rules:
                    tags.append(css_rules[c_name])

            sub = translate(child)
            if not sub:
                continue

            for tag in tags:
                s += '\\'
                s += tag
                s += '{'
            s += sub

            for i in range(len(tags)):
                s += '}'
            if child.name == 'p':
                s += '\n\n'
        else:
            s += str(child.text)
    return s


parser = argparse.ArgumentParser()
parser.add_argument('zipfile', type=pathlib.Path)
args = parser.parse_args()

with zipfile.ZipFile(args.zipfile, mode='r') as archive:
    for path in archive.namelist():
        soup = BeautifulSoup(open(path), 'lxml')
        css_rules = {}
        for style in soup.find_all('style'):
            sheet = cssutils.parseString(style.getText())
            for rule in sheet:
                if rule.selectorText[0] != '.':
                    continue
                name = rule.selectorText[1:]
                for key in ['font-style', 'font-weight']:
                    if key in rule.style:
                        if key == 'font-style' and rule.style[key] == 'normal':
                            continue
                        elif key == 'font-weight' and rule.style[key] == '400':
                            continue
                        if name in css_rules:
                            print(name, key)
                        if key == 'font-style':
                            css_rules[name] = 'textit'
                        else:
                            css_rules[name] = 'textbf'

        print(translate(soup.find('body')))
