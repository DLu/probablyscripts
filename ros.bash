#!/usr/bin/env bash
alias success_sound='if [ $? -eq 0 ]; then aplay /home/dlu/Sounds/smw_power-up.wav 2> /dev/null; true; else aplay /home/dlu/Sounds/smw_pipe.wav 2> /dev/null; false; fi'
alias fucking_catkin='catkin_make -DCMAKE_BUILD_TYPE=Release ; success_sound'

alias qwe='catkin build --this --no-deps --catkin-make-args run_tests; success_sound'
alias qwer='ros_test; success_sound'
alias list_plugins='rospack plugins --attrib=plugin '
alias subup='git submodule update --recursive'

alias rosprofile="rosrun --prefix 'valgrind --tool=callgrind' "
alias rosmemcheck="rosrun --prefix 'valgrind --tool=memcheck' "
alias fix_cpp_style="find -regextype egrep -regex '.*\.[ch](pp)?$' -exec astyle '{}' --style=allman --indent=spaces=2 --pad-oper --unpad-paren --pad-header --convert-tabs -n \;"
alias cpp_style_check="find -regextype egrep -regex '.*\.[ch](pp)?$' -exec rosrun roslint cpplint --filter -build/c++11,-runtime/references '{}' \; 2>&1 | grep -v 'Total errors' | grep -v 'Done processing'"


alias asdf='rosbuild -c --this'
alias zxcv='rosbuild --this --no-deps'
alias install_deps="rosdep_install"

export RCUTILS_CONSOLE_OUTPUT_FORMAT="[{name}]: {message}"
export RCUTILS_COLORIZED_OUTPUT=1
