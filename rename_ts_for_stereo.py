import os
import sys
from os import listdir
from os.path import isfile, join

if len(sys.argv) < 2:
    print("dataset dir path needed as argument")
    exit(1)

data_dir = sys.argv[1]

folder_name = "left_stereo"
os.chdir(os.path.join(data_dir, folder_name))
print(os.getcwd())
 
for count, f in enumerate(os.listdir()):
    f_name, f_ext = os.path.splitext(f)
    f_name = str(int(float(f_name)*1e9))
 
    new_name = f'{f_name}{f_ext}'
    os.rename(f, new_name)
os.chdir(os.path.join(os.getcwd(), '../'))

folder_name = "right_stereo"
os.chdir(os.path.join(os.getcwd(), folder_name))
print(os.getcwd())
 
for count, f in enumerate(os.listdir()):
    f_name, f_ext = os.path.splitext(f)
    f_name = str(int(float(f_name)*1e9))
 
    new_name = f'{f_name}{f_ext}'
    os.rename(f, new_name)
os.chdir(os.path.join(os.getcwd(), '../'))


