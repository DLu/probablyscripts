import click
import configparser
from io import StringIO
import pathlib
from ruamel.yaml import YAML

PRECOMMIT_FILENAME = '.pre-commit-config.yaml'

YAML_FORMAT_OPTIONS = {
    'mapping': 2,
    'sequence': 2,
    'offset': 0,
}
YAML_ARGS = ['--width', '120', '--implicit_start', '--implicit_end']
for k, v in YAML_FORMAT_OPTIONS.items():
    YAML_ARGS += [f'--{k}', f'{v}']


def find_git_directory():
    p = pathlib.Path().resolve()
    while not (p / '.git').exists():
        p = p.parent
    return p


class PrecommitConfig(dict):
    def __init__(self, root):
        self.precommit_file = root / PRECOMMIT_FILENAME
        self.yaml = YAML()
        self.yaml.indent(**YAML_FORMAT_OPTIONS)

        if self.precommit_file.exists():
            config = self.yaml.load(open(self.precommit_file))
            self.update(config)
        else:
            self['repos'] = []

    def get_hooks(self, search_key=''):
        for repo in self['repos']:
            for hook in repo.get('hooks', []):
                if search_key in hook['id']:
                    yield hook

    def write(self):
        self.yaml.dump(dict(self), open(self.precommit_file, 'w'))


class SetupConfig(configparser.ConfigParser):
    def __init__(self, root):
        configparser.ConfigParser.__init__(self)
        self.cfg_path = root / 'setup.cfg'
        if self.cfg_path.exists():
            self.read(self.cfg_path)
            self.changed = False
        else:
            self.changed = True

    def get_value(self, section_name, key):
        if self.has_section(section_name):
            return self[section_name].get(key)

    def set_value(self, section_name, key, value):
        if not self.has_section(section_name):
            self.add_section(section_name)
            self.changed = True

        old_val = self[section_name].get(key)
        if old_val != value:
            self.set(section_name, key, value)
            self.changed = True

    def save(self):
        if not self.changed:
            return

        if self.cfg_path.exists():
            click.secho(f'Updating {self.cfg_path.name}', fg='blue')
        else:
            click.secho(f'Creating {self.cfg_path.name}', fg='blue')

        string_file = StringIO()
        self.write(string_file, space_around_delimiters=False)
        string_file.seek(0)
        contents = string_file.read()
        if contents.endswith('\n\n'):
            contents = contents[:-1]
        with open(self.cfg_path, 'w') as f:
            f.write(contents)
