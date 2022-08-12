#!/usr/bin/env bash

alias hosts_timeout.py='sudo env PATH=$PATH hosts_timeout.py'
alias latex-mk='latex-mk --pdflatex'
alias gitst='git status .'
alias gitdiff='git difftool -g -d'
alias gitundo="git reset --soft 'HEAD^'"
alias gitredo='git commit -c ORIG_HEAD'
alias gitrecent='git for-each-ref --sort=-committerdate refs/heads/ | tac'
alias superpush='git push -u origin `git rev-parse --abbrev-ref HEAD`'
alias list_installed='dpkg --get-selections | grep -v deinstall | awk -F" " '"'"'{ print $1 }'"'"' | grep'
PS1="\[\e]2;\h | \w \a\]! \W/ > "

alias pip_v='pip show $1 '

alias ls='ls -h --color=auto'
alias check_size='du -hs'

alias ackc='ack -c -l --sort-files'
alias ack='ack --sort-files'

alias atom_root='atom `git rev-parse --show-toplevel`'
alias rip_mp3='youtube-dl -x --audio-format mp3 -o "%(title)s.%(ext)s" '

#PS1="! \W/ > "

alias cmdf='history | grep '
alias please='sudo'
source /home/dlu/Projects/probablyscripts/ros.bash

export PYTHONPATH=$PYTHONPATH:/home/dlu/Projects/probablyscripts/
