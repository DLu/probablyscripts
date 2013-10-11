import subprocess

def execute(command):
    subprocess.Popen(command, \
      stderr=subprocess.STDOUT, stdout=subprocess.PIPE).communicate()[0]
