#!/bin/bash
cd $CATKIN_PACKAGE_PATH/autonomous_drone_package/www
python -m http.server 8080
