import bs4
import pathlib


def find_by_class(soup, name, class_name):
    return soup.find(name, {'class': class_name})


def find_all_by_class(soup, name, class_name):
    return soup.find_all(name, {'class': class_name})


def is_string_element(element):
    return isinstance(element, bs4.NavigableString)


class BeautifulParser(bs4.BeautifulSoup):
    def __init__(self, obj):
        if isinstance(obj, pathlib.Path):
            obj = open(obj)
        bs4.BeautifulSoup.__init__(self, obj, 'lxml')

    def find_by_class(self, name, class_name):
        return find_by_class(self, name, class_name)

    def find_all_by_class(self, name, class_name):
        return find_all_by_class(self, name, class_name)
