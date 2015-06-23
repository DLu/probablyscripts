#!/usr/bin/env bash

alias fucking_catkin='catkin_make -DCMAKE_BUILD_TYPE=Release ; if [ $? -eq 0 ]; then aplay /home/dlu/Sounds/smw_power-up.wav 2> /dev/null; else aplay /home/dlu/Sounds/smw_pipe.wav 2> /dev/null; fi'
alias list_plugins='rospack plugins --attrib=plugin '

alias add_ros_path='export ROS_PACKAGE_PATH=/home/dlu/ros:$ROS_PACKAGE_PATH'
alias fuerte='source /opt/ros/fuerte/setup.bash ;                                                      add_ros_path'
alias groovy='source /opt/ros/groovy/setup.bash ; source /home/dlu/Catkin/groovy_nav/devel/setup.bash; add_ros_path'
alias hydro='source /opt/ros/hydro/setup.bash   ; source /home/dlu/Catkin/hydro_nav/devel/setup.bash;  add_ros_path'
alias swri='source /opt/ros/hydro/setup.bash    ; source /home/dlu/Catkin/swri/devel/setup.bash;       add_ros_path'
alias nasa='source /opt/ros/hydro/setup.bash    ; source /home/dlu/Catkin/nasa/devel/setup.bash;       add_ros_path'
alias locus='source /opt/ros/indigo/setup.bash   ; source /home/dlu/Catkin/locus/devel/setup.bash;      add_ros_path'
alias skyskysky='source /opt/ros/hydro/setup.bash   ; source /home/dlu/Catkin/skyskysky/devel/setup.bash;      add_ros_path'


