import subprocess

def git_cmd(args, location):
    p = subprocess.Popen(['git'] + args, cwd=location, stdout=subprocess.PIPE)
    return p.communicate()[0]

def get_remotes(location):
    remote_names = git_cmd(['remote'], location).strip().split('\n')
    remotes = {}
    for r in remote_names:
        s = git_cmd(['config', '--get', 'remote.%s.url'%r], location)
        remotes[r] = s.strip()
    return remotes

