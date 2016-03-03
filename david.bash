#!/usr/bin/env bash

alias hosts_timeout.py='sudo env PATH=$PATH hosts_timeout.py'
alias latex-mk='latex-mk --pdflatex'
alias gitst='git status .'
alias gitdiff='git difftool -g -d'
alias gitundo="git reset --soft 'HEAD^'"
alias gitredo='git commit -c ORIG_HEAD'
alias gitrecent='git for-each-ref --sort=-committerdate refs/heads/'
alias superpush='git push -u origin `git rev-parse --abbrev-ref HEAD`'
alias seas='ssh dvl1@ssh.seas.wustl.edu'
alias seas2='ssh dvl1@ssh2.seas.wustl.edu'
alias sshai='ssh cse511a@shell.cec.wustl.edu'
alias cec='ssh dlu@shell.cec.wustl.edu'
alias list_installed='dpkg --get-selections | grep -v deinstall | awk -F" " '"'"'{ print $1 }'"'"' | grep'
PS1="\[\e]2;\h | \w \a\]! \W/ > "

alias ls='ls -h'

#PS1="! \W/ > "

alias cmdf='history | grep '
source /home/dlu/Projects/probablyscripts/ros.bash

