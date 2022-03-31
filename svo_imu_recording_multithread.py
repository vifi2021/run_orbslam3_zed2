import pyzed.sl as sl
import cv2, csv
import numpy as np
import math
import logging
import sys
import time
from time import ctime
import threading
import signal
import getopt
from datetime import datetime
import os

zed = sl.Camera()
exit_event = threading.Event()

def interrupt_handler(sig, frame):
    # End camera recording
    global zed
    exit_event.set()
    zed.disable_recording()
    zed.close()
    sys.stdout.flush()
    sys.exit(0)

class TimeHandler:
    def __init__(self):
        self.t_imu = sl.Timestamp()
        self.t_baro = sl.Timestamp()
        self.t_mag = sl.Timestamp()

    def new_data(self, sensor):
        if (isinstance(sensor, sl.IMUData)):
            new_ = (sensor.timestamp.get_microseconds() > self.t_imu.get_microseconds())
            if new_:
                self.t_imu = sensor.timestamp
            return new_
        elif (isinstance(sensor, sl.MagnetometerData)):
            new_ = (sensor.timestamp.get_microseconds() > self.t_mag.get_microseconds())
            if new_:
                self.t_mag = sensor.timestamp
            return new_
        elif (isinstance(sensor, sl.BarometerData)):
            new_ = (sensor.timestamp.get_microseconds() > self.t_baro.get_microseconds())
            if new_:
                self.t_baro = sensor.timestamp
            return new_

# def current_time():
#     newcur = ctime().split()[:]
#     print(newcur)
#     print('-'.join(str(x) for x in newcur))
#     return '-'.join(str(x) for x in newcur)

# def write_log_file(current_time):
#     file_name  = "/media/hans/T7/SLAM_data/RAN_SLAM/myOwn/home_try/" + current_time + ".log"
#     open(file_name, 'w')
#     logging.basicConfig(filename= file_name, level = logging.INFO)

def get_res_framerate (resolution_string: str, frame_rate: str):
    cleaned = resolution_string.lower()
    res = sl.RESOLUTION.VGA
    if cleaned in ('wvga', 'vga'):
        res = sl.RESOLUTION.VGA
    elif cleaned in ('hd'):
        res = sl.RESOLUTION.HD720
    elif cleaned in ('fullhd', 'fhd'):
        res = sl.RESOLUTION.HD1080
    elif cleaned in ('4k', '2k', '2.2k'):
        res = sl.RESOLUTION.HD2K
    else:
        print('Incorrect Resolution requested, use WVGA, HD, FULLHD, 4K')
        usage()
        exit()
    fps_request = int(frame_rate)
    rate = 100
    if fps_request not in (15, 30, 60, 100):
        print('Incorrect framerate requested, use 15, 30, 60, 100')
        usage()
        exit()
    elif fps_request == 15:
         rate = 15
    elif fps_request == 30 and res in (sl.RESOLUTION.VGA, sl.RESOLUTION.HD720, sl.RESOLUTION.HD1080):
        rate = 30
    elif fps_request == 60 and res in (sl.RESOLUTION.VGA, sl.RESOLUTION.HD720):
        rate = 60
    elif fps_request == 100 and res == sl.RESOLUTION.VGA:
        rate = 100
    else:
        print('Something incredible has happened, you have somehow broken everything')
        usage()
        exit()
    print(res, rate)
    return res, rate


def printSensorParameters(sensor_parameters):
    if sensor_parameters.is_available:
        print("*****************************")
        print("Sensor type: " + str(sensor_parameters.sensor_type))
        print("Max rate: "  + str(sensor_parameters.sampling_rate) + " "  + str(sl.SENSORS_UNIT.HERTZ))
        print("Range: "  + str(sensor_parameters.sensor_range) + " "  + str(sensor_parameters.sensor_unit))
        print("Resolution: " + str(sensor_parameters.resolution) + " "  + str(sensor_parameters.sensor_unit))
        if not math.isnan(sensor_parameters.noise_density):
            print("Noise Density: "  + str(sensor_parameters.noise_density) + " " + str(sensor_parameters.sensor_unit) + "/√Hz")
        if not math.isnan(sensor_parameters.random_walk):
            print("Random Walk: "  + str(sensor_parameters.random_walk) + " " + str(sensor_parameters.sensor_unit) + "/s/√Hz")



def zed_cam_run(runtime):
    print('enter thread of camera')
    global zed
    while True:
        # print(zed.grab(runtime))
        if zed.grab(runtime) == sl.ERROR_CODE.SUCCESS :
            # print("recording...")
            pass
        if exit_event.is_set():
            break
    print("zed safely closing before exiting.")



def imu_cam_run(ts_handler, sensors_data, imu_out_file):
    print('enter thread of imu')
    global zed
    things_to_write = []
    while True:
        if exit_event.is_set():
            imu_out_file.writelines(things_to_write)
            imu_out_file.close()
            print('imu_out_file is closed')
            break
        if zed.get_sensors_data(sensors_data, sl.TIME_REFERENCE.CURRENT) == sl.ERROR_CODE.SUCCESS :
            # ts = zed.get_timestamp(sl.TIME_REFERENCE.CURRENT).get_nanoseconds() / 1000000000
            # ts_str = "{:.9f}".format(ts)
            # ts_str = ts_str.replace('.', '')
            # Check if the data has been updated since the last time
            # IMU is the sensor with the highest rate
            if ts_handler.new_data(sensors_data.get_imu_data()):
                ts = sensors_data.get_imu_data().timestamp.get_nanoseconds() / 1000000000
                ts_str = "{:.9f}".format(ts)
                ts_str = ts_str.replace('.', '')

                # quaternion = sensors_data.get_imu_data().get_pose().get_orientation().get()
                # logging.info(" \t Orientation: [ Ox: {0}, Oy: {1}, Oz {2}, Ow: {3} ]".format(quaternion[0], quaternion[1], quaternion[2], quaternion[3]))
                
                linear_acceleration = sensors_data.get_imu_data().get_linear_acceleration()
                # logging.info(" \t Acceleration: [ {0} {1} {2} ] [m/sec^2]".format(linear_acceleration[0], linear_acceleration[1], linear_acceleration[2]))

                angular_velocity = sensors_data.get_imu_data().get_angular_velocity()
                # logging.info(" \t Angular Velocities: [ {0} {1} {2} ] [deg/sec]".format(angular_velocity[0], angular_velocity[1], angular_velocity[2]))

                # if ts_handler.new_data(sensors_data.get_magnetometer_data()):
                #     magnetic_field_calibrated = sensors_data.get_magnetometer_data().get_magnetic_field_calibrated()
                #     # logging.info(" - Magnetometer\n \t Magnetic Field: [ {0} {1} {2} ] [uT]".format(magnetic_field_calibrated[0], magnetic_field_calibrated[1], magnetic_field_calibrated[2]))
                
                # if ts_handler.new_data(sensors_data.get_barometer_data()):
                #     magnetic_field_calibrated = sensors_data.get_barometer_data().pressure
                #     # logging.info(" - Barometer\n \t Atmospheric pressure: {0} [hPa]".format(sensors_data.get_barometer_data().pressure))

                # record to txt file
                # things_to_write.append(','.join(list(map(str, [ts_str, math.radians(angular_velocity[0]), math.radians(angular_velocity[1]), math.radians(angular_velocity[2]), linear_acceleration[0], linear_acceleration[1], linear_acceleration[2]])))+'\n')
                things_to_write.append("{},{},{},{},{},{},{}\n".format(ts_str, math.radians(angular_velocity[0]), math.radians(angular_velocity[1]), math.radians(angular_velocity[2]), linear_acceleration[0], linear_acceleration[1], linear_acceleration[2]))
                
        # time.sleep(5)
        # print("logging imu")



def main(argv):
    global zed

    if len(sys.argv) < 2:
        print("need output_path as argument")
        exit(1)

    output_path = argv[1]
    if not os.path.exists(output_path):
        # Create a new directory because it does not exist 
        os.makedirs(output_path)
        print("The new directory is created!")

    now = datetime.now()
    dt_string = now.strftime("%m_%d_%Y__%H_%M_%S")
    # write_log_file(dt_string)
    imu_out_file_name = "imu_"+dt_string+".txt"

    imu_out_file = open(os.path.join(output_path, imu_out_file_name),"w")
    imu_out_file.write("# timestamp[ns] w.x[rad/s] w.y[rad/s] w.z[rad/s] a.x[m/s^2] a.y[m/s^2] a.z[m/s^2]\n")
    
    #zed = sl.Camera()
    init_params = sl.InitParameters()
    #init_params.depth_mode = sl.DEPTH_MODE.NONE
    init_params.depth_mode = sl.DEPTH_MODE.ULTRA

    # possible_res_string = "fhd"
    possible_res_string = 'vga'
    possible_frame_string = "30"

    signal.signal(signal.SIGINT, interrupt_handler)

    init_params.camera_resolution = sl.RESOLUTION.HD1080
    init_params.camera_fps = 30
    # init_params.coordinate_units = sl.UNIT.MILLIMETER
    # init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP

    # try:
    #     opts, args = getopt.getopt(argv, "ho:r:f:", ["output=", "resolution=", "framerate="])
    # except getopt.GetoptError:
    #     usage()
    #     sys.exit(2)

    # # if len(argv) == 0:
    #     # print('Using default values of WVGA at 100fps and defualt output name of date time')

    # for opt, arg in opts:
    #     if opt == '-h':
    #         usage()
    #         sys.exit()
    #     elif opt in ('-r', '--resolution'):
    #         possible_res_string = arg
    #     elif opt in ('-f', '--framerate'):
    #         possible_frame_string = arg
    #     elif opt in ('-o', '--output'):
    #         output_name = arg
    #     else:
    #         print('Unrecognised option')
    #         usage()
    #         exit()

    init_params.camera_resolution, init_params.camera_fps = get_res_framerate(possible_res_string, possible_frame_string)
    print('Resolution: {0}, Frame rate: {1}'.format(init_params.camera_resolution, init_params.camera_fps))
    

    status = zed.open(init_params)
    if status != sl.ERROR_CODE.SUCCESS:
        print(repr(status))
        zed.close() 
        exit(1)
    
    info = zed.get_camera_information()
    cam_model = info.camera_model

    # logging.info("Camera Model: " + str(cam_model))
    # logging.info("Serial Number: " + str(info.serial_number))
    # logging.info("Camera Firmware: " + str(info.camera_configuration.firmware_version))
    # logging.info("Sensors Firmware: " + str(info.sensors_configuration.firmware_version))
    
    printSensorParameters(info.sensors_configuration.accelerometer_parameters) # accelerometer configuration
    printSensorParameters(info.sensors_configuration.gyroscope_parameters) # gyroscope configuration
    
    ts_handler = TimeHandler()
    sensors_data = sl.SensorsData()
    # if cam_model == sl.MODEL.ZED: #check if cam information is ZED1
    #     print("This camera only supports ZED1")
    #     exit(1)

    svo_output = str(os.path.join(output_path, "{}_{}.svo".format(str(init_params.camera_resolution).split('.')[-1], dt_string)))
    recording_param = sl.RecordingParameters(svo_output, sl.SVO_COMPRESSION_MODE.H264)
    err = zed.enable_recording(recording_param)

    if err != sl.ERROR_CODE.SUCCESS:
        print('Enable Recording failed')
        print(repr(err))
        exit(1)

    runtime = sl.RuntimeParameters()
    runtime.sensing_mode = sl.SENSING_MODE.FILL
    
    thread1 = threading.Thread(target= imu_cam_run, args = (ts_handler, sensors_data, imu_out_file,))
    thread2 = threading.Thread(target = zed_cam_run, args = (runtime,))

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    





if __name__ == '__main__':
    main(sys.argv[:])

