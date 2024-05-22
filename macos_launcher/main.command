#!/usr/bin/env bash
ver=0.5.1
main=$(basename "$0" .command)
echo -ne "\033c\033]0;$main v$ver\a"
read -rp "Drag input (and/or baseline) files here and press enter: " x
echo -n
echo -ne "\033cLoading...\r"
eval "\"$(dirname "$0")/src/$main\" $x"
