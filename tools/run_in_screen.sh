#!/bin/bash

# This script simply starts a screen session with the runservermanager.py script.
# It will bind to the values in settings.cfg
screen -dm -S ssm python ../runservermanager.py
