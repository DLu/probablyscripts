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

    def write(self):
        self.yaml.dump(dict(self), open(self.precommit_file, 'w'))
