# to generate a txt file that associate rgb and depth frames for zed, (non-trivial, since it is already synchronized)
import os
from os import listdir
from os.path import isfile, join
import sys


data_dir = sys.argv[1]
filename = os.path.join(data_dir, data_dir.split('/')[0]+"_left_timestamps.txt")
outfile = open(filename, 'w')

# read all the rgb files
rgb_frame_names = sorted([f for f in listdir(data_dir+'/left_stereo/') if isfile(join(data_dir+'/left_stereo/', f))], key=lambda x: float(x[:-4]))
# print(rgb_frame_names)

# use the rgb file names to construct txt file
for rgb_frame_name in rgb_frame_names:
    line = rgb_frame_name[:-4]+'\n'
    outfile.write(line)


outfile.close()
