# How to run ORB-SLAM3
This is a notes on how to run orbslam3 with zed2 data
supported mode:
- RGBD
- Stereo
- Stereo-Inertial

Data used:
- Left camera frames
- Right camera frames
- IMU data (accelerometer + angular velocity)
-----------------------------------------------------------------
# Compile ORB-SLAM3
following https://github.com/UZ-SLAMLab/ORB_SLAM3 for more details.
For dependency, I use:
- Pangolin
- OpenCV 3.4 (with contrib module)
- Eigen 3.3.9

------------------------------------------------------------------
# Visual SLAM mode (Same as ORB-SLAM2)
Pipeline of creating myOwn dataset:

1. record ZED2 svo, ZED2 imu (accelerometer + angular velocity) and collect FTM (ntp synchronized)
	```
	$ python3 record_svo_imu_multithread.py [dataset_dir_path]
	```

2. create a folder for your collected sequence 
	```
	$ cd ~/Documents/ORB-SLAM2/dataset/myOwn/
	$ cd [dataset_dir_path] && mkdir depth left right && cd ..
	```

3. under myOwn/, extract left and right rgb and depth16 from svo buy running:
	```
	$ python3 export_svo_customized.py [svo file path] [dataset_dir_path]/left/ 4
	```

4. under myOwn/, associate depth and rgb by running:
	```
	$ python3 associate_rgb_depth.py [dataset_dir_path]
	```
	this will generate a associated txt file for left frames and depth images

5. prepare the .yaml file like using the TUM or EuRoC format

6. To run rgbd mode:
go to ORB-SLAM3/ directoy and run
	```
	$ ./Examples/RGB-D/rgbd_tum [Vocabulary/ORBvoc.txt] [dataset/myOwn/dir_of_your_yaml] [dataset/myOwn/created_dir/] [dataset/myOwn/dir_of_the_generated_associated.txt] 
	```	
	in particular:
	```
	$ ./Examples/RGB-D/rgbd_tum  Vocabulary/ORBvoc.txt /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/ymal_config_files/visual_only_rgbd_TUM_orbslam3.yaml /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/winlab_ftm_1/ /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/winlab_ftm_1/winlab_ftm_1_associated.txt
	```
-----------------------------------------------------

# V-I SLAM mode 

7. copy left/ and right/ as left_stereo/ and right_stereo/, then run rename_ts_for_stereo.py
	$ cd [dataset_dir_path]
	$ cp -r left/ left_stereo/
	$ cp -r right/ right_stereo # or mv right/ right_stereo/
	$ cd ..
	$ python3 rename_ts_for_stereo.py [dataset_dir_path]

8. generate timestamp files
	$ python3 get_left_timestamps.py [dataset_dir_path]

9. if necessary, change the timestamp in the imu file so that no decimal exist.

10. make sure imu timestamp starts ealier

# run V-I mode following TUM-VI format (so far haven't succeed)
<!-- Usage: ./stereo_inertial_tum_vi [path_to_vocabulary] [path_to_settings_ymal] [path_to_image_folder_1] [path_to_image_folder_2] [path_to_times_file_for_images] [path_to_imu_data(trajectory_file_name)]

./Examples/Stereo-Inertial/stereo_inertial_tum_vi Vocabulary/ORBvoc.txt Examples/Stereo-Inertial/TUM-VI.yaml /media/hans/T7/SLAM_data/TUM_V-I/dataset-corridor1_512_16/mav0/cam0/data /media/hans/T7/SLAM_data/TUM_V-I/dataset-corridor1_512_16/mav0/cam1/data Examples/Stereo-Inertial/TUM_TimeStamps/dataset-corridor1_512.txt Examples/Stereo-Inertial/TUM_IMU/dataset-corridor1_512.txt

./Examples/Stereo-Inertial/stereo_inertial_tum_vi Vocabulary/ORBvoc.txt /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/winlab_ftm_2/winlab_ftm_2_VI.yaml /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/winlab_ftm_2/left_stereo /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/winlab_ftm_2/right_stereo  /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/winlab_ftm_2/winlab_ftm_2_left_timestamps.txt /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/winlab_ftm_2/imu_02_11_2022__19_03_47.txt

./Examples/Stereo-Inertial/stereo_inertial_tum_vi Vocabulary/ORBvoc.txt /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/home_try/home_try_VI.yaml /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/home_try/left_stereo /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/home_try/right_stereo  /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/home_try/home_try_left_timestamps.txt /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/home_try/imu_03_13_2022__16_02_48.txt -->

# run Stereo mode following EuRoc format
Usage: ./stereo_inertial_euroc [path_to_vocabulary] [path_to_settings] [path_to_sequence_folder] [path_to_timestamp_file]

./Examples/Stereo/stereo_euroc Vocabulary/ORBvoc.txt /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/ymal_config_files/EuRoC_vga.yaml /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/home_try_vga/ /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/home_try_vga/home_try_vga_left_timestamps.txt  


# run Stereo-V-I mode following EuRoC format
Usage: ./stereo_inertial_euroc [path_to_vocabulary] [path_to_settings] [path_to_sequence_folder] [path_to_timestamp_file] [path_to_imu_file]

run example:
./Examples/Stereo-Inertial/stereo_inertial_euroc Vocabulary/ORBvoc.txt Examples/Stereo-Inertial/EuRoC.yaml /media/hans/T7/SLAM_data/EuRoc/MH_01_easy/ Examples/Stereo-Inertial/EuRoC_TimeStamps/MH01.txt 

run on my dataset:
first comment the code,

./Examples/Stereo-Inertial/stereo_inertial_euroc Vocabulary/ORBvoc.txt /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/ymal_config_files/visual_imu_stereo_EuRoC_orbslam3.yaml /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/winlab_ftm_3/ /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/winlab_ftm_3/winlab_ftm_3_left_timestamps.txt /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/winlab_ftm_3/imu_03_14_2022__12_05_26.txt 
