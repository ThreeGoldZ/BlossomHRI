import time
import numpy as np
from robot import Robot
from config import ROBOT_330_LAB

def record_demonstration(duration=10, interval=0.01, save_path='demonstration.npy'):
    robot = Robot(config_dict=ROBOT_330_LAB)
    #robot.enable_torque()
    
    data = []
    start_time = time.time()
    print("Recording demonstration... Move the robot manually.")
    
    while time.time() - start_time < duration:
        angles = robot.get_motor_angles([5, 6])  # Only motor 1 and 2
        timestamp = time.time() - start_time
        data.append([timestamp] + angles)
        time.sleep(interval)
    
    np.save(save_path, np.array(data))
    print(f"Saved demonstration to {save_path}")
    robot.clean_shutdown()

def replay_demonstration(load_path='demonstration.npy'):
    robot = Robot(config_dict=ROBOT_330_LAB)
    robot.enable_torque()
    robot.set_speed(30,300)

    data = np.load(load_path)  # shape: (N, 3) -> [time, angle1, angle2]
    timestamps = data[:, 0]
    angles1 = data[:, 1]
    angles2 = data[:, 2]

    start_time = time.time()
    print("Replaying demonstration with interpolation...")

    while True:
        now = time.time() - start_time
        if now > timestamps[-1]:
            break

        # Linear interpolation
        angle1 = np.interp(now, timestamps, angles1)
        angle2 = np.interp(now, timestamps, angles2)

        # Move motors without duration (or set short constant)
        robot.move_motors_sync(args={5: angle1, 6: angle2}, duration={5:30, 6:30})
        #time.sleep(0.01)  # ~20 Hz refresh

    robot.clean_shutdown()
    print("Replay complete.")

if __name__ == "__main__":
    # Choose one at a time
    #record_demonstration(duration=15)
    replay_demonstration()
