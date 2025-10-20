import bs4
import click
import pathlib
import requests


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
        bs4.BeautifulSoup.__init__(self, obj, 'html.parser')

    def find_by_class(self, name, class_name):
        return find_by_class(self, name, class_name)

    def find_all_by_class(self, name, class_name):
        return find_all_by_class(self, name, class_name)


def get_page(url, stem, allow_cached=True, cache_folder='.html_cache', user_agent=None, email=None):
    cache_dir_path = pathlib.Path(cache_folder)
    cache_dir_path.mkdir(exist_ok=True)
    cache_path = cache_dir_path / (stem + '.html')
    if allow_cached and cache_path.exists():
        contents = open(cache_path).read()
    else:
        headers = {}
        if user_agent:
            headers['User-Agent'] = user_agent
        if email:
            headers['From'] = email

        click.secho(f'Retrieving {url}', fg='bright_black')
        req = requests.get(url, headers=headers)
        contents = req.text

        with open(cache_path, 'w') as f:
            f.write(contents)

    return BeautifulParser(contents)
