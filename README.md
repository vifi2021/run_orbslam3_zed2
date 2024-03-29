# Running ORB-SLAM3 with ZED2 RGBD+imu data
This is a memo on how to run orbslam3 with data (images and IMU data) collected on ZED2 Camera.

Supported mode:
- RGBD
- Stereo
- Stereo-Inertial

Data used:
- Left camera frames, VGA @ 30 fps
- Right camera frames, VGA @ 30 fps
- Depth map, VGA @ 30 fps
- IMU data (accelerometer + angular velocity), 90 Hz
-----------------------------------------------------------------
## Compile ORB-SLAM3
Follow https://github.com/UZ-SLAMLab/ORB_SLAM3 for more detail.
For dependency, I use:
- Pangolin
- OpenCV 3.4 (with contrib module)
- Eigen 3.3.9

------------------------------------------------------------------
## prepare the data
Pipeline of creating myOwn dataset:

1. record ZED2 svo, ZED2 imu (accelerometer + angular velocity) and collect FTM (ntp synchronized)
	```
	$ cd ~/Documents/ORB-SLAM2/dataset/myOwn/
	$ python3 svo_imu_recording_multithread.py [dataset_dir_path]
	# a .svo file and .txt file will be stored to [dataset_dir_path]
	```

2. Extract left frame, right frame and depth map
	```
	$ cd [dataset_dir_path] && mkdir depth left right && cd ..
	
	# under myOwn/, extract left and right rgb and depth16 from svo buy running:
	$ python3 export_svo_customized.py [svo file path] [dataset_dir_path]/left/ 4
	```

3. Prepare data for RGBD mode
	```
	# under myOwn/, associate depth and rgb by running:
	$ python3 associate_rgb_depth.py [dataset_dir_path]
	# this will generate a associated txt file for left frames and depth images
	```

4. prepare data for Stereo and Stereo-Inertial mode
	```
	$ cd [dataset_dir_path]
	$ cp -r left/ left_stereo/
	$ cp -r right/ right_stereo # or mv right/ right_stereo/
	$ cd ..
	# in ORB-SLAM3 Stereo/Stereo-Inertial mode, timestamps don't have decimals
	$ python3 rename_ts_for_stereo.py [dataset_dir_path] 
	$ python3 get_left_timestamps.py [dataset_dir_path]
	```

5. Optional, downsample the RGBD timestamps to lower frame rate
	```
	$ bash down_sample_ts.sh [downsample factor] [input_timestamp_txt] [output_timestamp_30/factor_txt] 
	```
-----------------------------------------------------

## Prepare the .yaml files 
Follow the TUM or EuRoC format. Modify camera intrinsics according to the camera model.

Notice: The Transformation from camera frame to imu frame (T_imu_cam) must be correct. In my dataset, the camera frame and imu frame is the same (origin: lefteye, x: right, y: down, z: forward)

-----------------------------------------------------

## Necessary modifications on ORB-SLAM3's code

There are several necessary modifications.
- In ORB_SLAM3/Examples/Stereo/stereo_euroc.cc:73
	```
	// string pathCam0 = pathSeq + "/mav0/cam0/data";
	// string pathCam1 = pathSeq + "/mav0/cam1/data";
	// change to:
	string pathCam0 = pathSeq + "/left_stereo";
	string pathCam1 = pathSeq + "/right_stereo";
	```
- In ORB_SLAM3/Examples/Stereo-Inertial/stereo_inertial_euroc.cc:88
	```
	// string pathCam0 = pathSeq + "/mav0/cam0/data";
	// string pathCam1 = pathSeq + "/mav0/cam1/data";
	// string pathImu = pathSeq + "/mav0/imu0/data.csv";
	// change to:
	string pathCam0 = pathSeq + "/left_stereo";
	string pathCam1 = pathSeq + "/right_stereo";
	string pathImu(argv[(2*seq) + 5]);
	```
- In ORB_SLAM3/src/Optimizer.cc:3144 and 3118
	```
	// change to 
	if(!pKFi->mpImuPreintegrated) {
		std::cout << "Not preintegrated measurement" << std::endl;
		continue;
	}
	```
- In ORB_SLAM3/src/System.cc:318
	```
	// Sophus::SE3f Tcw = mpTracker->GrabImageStereo(imLeftToFeed,imRightToFeed,timestamp,filename);
	// no need to rectify the image in the code, zed2 provided images that are already rectified. 
	Sophus::SE3f Tcw = mpTracker->GrabImageStereo(imLeft,imRight,timestamp,filename);
	```
- In ORB_SLAM3/src/Tracking.cc: 607 and 1345
	```
	// mImuPer = 0.001; //1.0 / (double) mImuFreq;
	// the imu period should be defined by the frequency in the yaml file
	mImuPer = 1.0 / (double) mImuFreq;
	```


-----------------------------------------------------

## Run RGBD mode following TUM format:
go to ORB-SLAM3/ directoy and run:
```
$ ./Examples/RGB-D/rgbd_tum [Vocabulary/ORBvoc.txt] [dataset/myOwn/dir_of_your_yaml] [dataset/myOwn/created_dir/] [dataset/myOwn/dir_of_the_generated_associated.txt] 
```
	
in particular:
```
$ ./Examples/RGB-D/rgbd_tum  Vocabulary/ORBvoc.txt /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/ymal_config_files/visual_only_rgbd_TUM_orbslam3.yaml /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/winlab_ftm_1/ /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/winlab_ftm_1/winlab_ftm_1_associated.txt
```
-----------------------------------------------------

<!-- # run V-I mode following TUM-VI format (so far haven't succeed) -->
<!-- Usage: ./stereo_inertial_tum_vi [path_to_vocabulary] [path_to_settings_ymal] [path_to_image_folder_1] [path_to_image_folder_2] [path_to_times_file_for_images] [path_to_imu_data(trajectory_file_name)]

./Examples/Stereo-Inertial/stereo_inertial_tum_vi Vocabulary/ORBvoc.txt Examples/Stereo-Inertial/TUM-VI.yaml /media/hans/T7/SLAM_data/TUM_V-I/dataset-corridor1_512_16/mav0/cam0/data /media/hans/T7/SLAM_data/TUM_V-I/dataset-corridor1_512_16/mav0/cam1/data Examples/Stereo-Inertial/TUM_TimeStamps/dataset-corridor1_512.txt Examples/Stereo-Inertial/TUM_IMU/dataset-corridor1_512.txt

./Examples/Stereo-Inertial/stereo_inertial_tum_vi Vocabulary/ORBvoc.txt /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/winlab_ftm_2/winlab_ftm_2_VI.yaml /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/winlab_ftm_2/left_stereo /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/winlab_ftm_2/right_stereo  /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/winlab_ftm_2/winlab_ftm_2_left_timestamps.txt /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/winlab_ftm_2/imu_02_11_2022__19_03_47.txt

./Examples/Stereo-Inertial/stereo_inertial_tum_vi Vocabulary/ORBvoc.txt /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/home_try/home_try_VI.yaml /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/home_try/left_stereo /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/home_try/right_stereo  /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/home_try/home_try_left_timestamps.txt /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/home_try/imu_03_13_2022__16_02_48.txt -->

## Run Stereo mode following EuRoc format
Usage: 
```
$./stereo_inertial_euroc [path_to_vocabulary] [path_to_settings] [path_to_sequence_folder] [path_to_timestamp_file]
```

For example:
```
$ ./Examples/Stereo/stereo_euroc Vocabulary/ORBvoc.txt /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/ymal_config_files/EuRoC_vga.yaml /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/home_try_vga/ /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/home_try_vga/home_try_vga_left_timestamps.txt  
```

## Run Stereo-Inertial mode following EuRoC format
Usage: 
```
$ ./stereo_inertial_euroc [path_to_vocabulary] [path_to_settings] [path_to_sequence_folder] [path_to_timestamp_file] [path_to_imu_file]
```

For example:
```
./Examples/Stereo-Inertial/stereo_inertial_euroc Vocabulary/ORBvoc.txt Examples/Stereo-Inertial/EuRoC.yaml /media/hans/T7/SLAM_data/EuRoc/MH_01_easy/ Examples/Stereo-Inertial/EuRoC_TimeStamps/MH01.txt 
```

run on my dataset:
first comment the code,

```
$ ./Examples/Stereo-Inertial/stereo_inertial_euroc Vocabulary/ORBvoc.txt /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/ymal_config_files/EuRoC_vga.yaml /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/apartment_loop/ /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/apartment_loop/apartment_loop_left_timestamps.txt /media/hans/T7/SLAM_data/RAN_SLAM/myOwn/apartment_loop/imu_04_05_2022__20_18_55.txt 
```
