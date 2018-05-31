import subprocess
import re
import yaml

DEVICE_PATTERN = re.compile('([^\s]+) (dis)?connected ([^\n]+)\n(( [^\n]+\n)+)', re.DOTALL)
CONFIG_PATTERN = re.compile('(\d+)x(\d+)\+(\d+)\+(\d+)')


def get_mapping(devices, config):
    keys0 = sorted(devices.keys())
    keys1 = sorted(config.keys())
    if len(keys0) == len(keys1):
        return dict(zip(keys0, keys1))
    m = {}
    print keys0, keys1
    return m


def get_current_config():
    output = subprocess.check_output(['xrandr'])
    devices = {}
    for x in DEVICE_PATTERN.findall(output):
        if x[1] == 'dis':
            continue
        name = x[0]
        m = CONFIG_PATTERN.search(x[2])
        if not m:
            print x[2]
        devices[name] = {'w': int(m.group(1)), 'h': int(m.group(2)), 'x': int(m.group(3)), 'y': int(m.group(4))}
        if 'primary' in x[2]:
            devices[name]['primary'] = True
    return devices


CONFIG = yaml.load(open('/home/dlu/.monitor_config.yaml'))
while True:
    commands_run = False
    DEVICES = get_current_config()
    for d_key, c_key in get_mapping(DEVICES, CONFIG).iteritems():
        current = DEVICES[d_key]
        desired = CONFIG[c_key]
        cmd = ['xrandr', '--output', d_key]
        if current.get('x', 0) != desired.get('x', 0) or current.get('y', 0) != desired.get('y', 0):
            cmd += ['--pos', '%dx%d' % (desired.get('x', 0), desired.get('y', 0))]
        if current.get('w', 0) != desired.get('w', 0) or current.get('h', 0) != desired.get('h', 0):
            cmd += ['--mode', '%dx%d' % (desired.get('w', 0), desired.get('h', 0))]
        if desired.get('primary', False) and current.get('primary', False) is False:
            cmd.append('--primary')
        if len(cmd) == 3:
            continue
        print cmd
        subprocess.call(cmd)
        commands_run = True
    print
    if not commands_run:
        break
# alias two_screen='xrandr --output HDMI1 --auto --pos 1920x180 --primary ; xrandr --output VGA1 --auto'
