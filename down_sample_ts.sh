# downsample the timestamp file from 30 fps to 30/r fps
# @param:
# $1: the down sample rate r
# $2: input timestamp file
# $3: output timestamp file
awk "NR % $1 == 0" $2 > $3
