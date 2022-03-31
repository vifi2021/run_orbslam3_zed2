# to generate a txt file that associate rgb and depth frames for zed, (non-trivial, since it is already synchronized)
from os import listdir
from os.path import isfile, join
import os
import sys


if len(sys.argv) < 2:
	print("dataset dir path needed as argument")
	exit(1)

data_dir = sys.argv[1]
filename = os.path.join(data_dir, data_dir.split('/')[-2]+"_associated.txt")

outfile = open(filename, 'w')

# read all the rgb files
rgb_frame_names = sorted([f for f in listdir(data_dir+'/left/') if isfile(join(data_dir+'/left/', f))], key=lambda x: float(x[:-4]))
# print(rgb_frame_names)

# use the rgb file names to construct txt file
for rgb_frame_name in rgb_frame_names:
	line = rgb_frame_name[:-4]+' left/'+rgb_frame_name+' '+rgb_frame_name[:-4]+' depth/'+rgb_frame_name+'\n'
	outfile.write(line)


outfile.close()

