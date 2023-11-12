#!/bin/bash
if [ -n "$PATH" ]; then
    old_PATH=$PATH:
    PATH=
    while [ -n "$old_PATH" ]; do
        x=${old_PATH%%:*}  # Get the first remaining entry
        case $PATH: in
            *:"$x":*) ;;  # Already there
            *) PATH=$PATH:$x;;  # Not there yet
        esac
        old_PATH=${old_PATH#*:}
    done
    PATH=${PATH#:}
    unset old_PATH x
fi
echo $PATH

