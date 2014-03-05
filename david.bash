#!/usr/bin/env bash

alias hosts_timeout.py='sudo env PATH=$PATH hosts_timeout.py'
alias latex-mk='latex-mk --pdflatex'
alias gitst='git status .'
alias gitdiff='git difftool -g -d'
alias fucking_catkin='catkin_make -DCMAKE_BUILD_TYPE=Release ; if [ $? -eq 0 ]; then aplay /home/dlu/Sounds/smw_power-up.wav 2> /dev/null; else aplay /home/dlu/Sounds/smw_pipe.wav 2> /dev/null; fi'
alias seas='ssh dvl1@ssh.seas.wustl.edu'
alias seas2='ssh dvl1@ssh2.seas.wustl.edu'
alias list_installed='dpkg --get-selections | grep -v deinstall | awk -F" " '"'"'{ print $1 }'"'"' | grep'
PS1="\[\e]2;\h | \w \a\]! \W/ > "
#PS1="! \W/ > "

