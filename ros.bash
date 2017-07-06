#!/usr/bin/env bash
alias success_sound='if [ $? -eq 0 ]; then aplay /home/dlu/Sounds/smw_power-up.wav 2> /dev/null; true; else aplay /home/dlu/Sounds/smw_pipe.wav 2> /dev/null; false; fi'
alias fucking_catkin='catkin_make -DCMAKE_BUILD_TYPE=Release ; success_sound'
alias friggin_catkin='catkin build ; success_sound'
alias asdf='catkin build --this; success_sound'
alias zxcv='catkin build --this --no-deps; success_sound'
alias qwer='ros_test; success_sound'
alias list_plugins='rospack plugins --attrib=plugin '
alias subup='git submodule update --recursive'
alias add_ros_path='export ROS_PACKAGE_PATH=/home/dlu/ros:$ROS_PACKAGE_PATH'
alias fuerte='source /opt/ros/fuerte/setup.bash ;                                                      add_ros_path'
alias groovy='source /opt/ros/groovy/setup.bash ; source /home/dlu/Catkin/groovy_nav/devel/setup.bash; add_ros_path'
alias hydro='source /opt/ros/hydro/setup.bash   ; source /home/dlu/Catkin/hydro_nav/devel/setup.bash;  add_ros_path'
alias swri='source /opt/ros/hydro/setup.bash    ; source /home/dlu/Catkin/swri/devel/setup.bash;       add_ros_path'
alias nasa='source /opt/ros/hydro/setup.bash    ; source /home/dlu/Catkin/nasa/devel/setup.bash;       add_ros_path'
alias locus='source /opt/ros/indigo/setup.bash   ; source /home/dlu/Catkin/locus/devel/setup.bash;      add_ros_path'
alias skyskysky='source /opt/ros/hydro/setup.bash   ; source /home/dlu/Catkin/skyskysky/devel/setup.bash;      add_ros_path'
alias indigo='source /opt/ros/indigo/setup.bash ; add_ros_path'
alias jadenav='source /opt/ros/jade/setup.bash   ; source /home/dlu/Catkin/jade_nav/devel/setup.bash;  add_ros_path'

alias rosdebug="rosrun --prefix 'gdb -ex run --args' "
alias rosprofile="rosrun --prefix 'valgrind --tool=callgrind' "
alias rosmemcheck="rosrun --prefix 'valgrind --tool=memcheck' "
alias cpp_style="find -regextype egrep -regex '.*\.[ch](pp)?$' -exec astyle '{}' --style=allman --indent=spaces=4 --pad-oper --unpad-paren --pad-header --convert-tabs -n \;"
alias install_deps="rosdep install --ignore-src -y -r --from-paths "
