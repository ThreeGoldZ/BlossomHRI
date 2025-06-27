from robot import *
from config import *
import time
import Touch2Gesture as tg

from log_conf import logger


from flask import Flask, request, jsonify

app = Flask(__name__)

def runTest():
    my_robot = Robot(config_dict=ROBOT_330_LAB)
    my_robot.set_speed(2,2)
    logger.info("Starting positions")
    my_robot.check_motor_status(["all"])
    my_robot.enable_torque()
    my_robot.move_motors_sync2(args={1:0, 2:0, 3:0, 4:0, 5:0, 6:150}, duration={1:1000, 2:500, 3:500, 4:500,5:500,6:500})
    logger.info("Result of move to 150")
    #my_robot.check_motor_status(["all"])
    logger.info("Sleep 2")
    time.sleep(10)
   

    my_robot.move_motors_sync2(args={1:-90, 2:-40, 3:-40, 4:0, 5:60, 6:90}, duration={1:1000, 2:1000, 3:1000, 4:1000,5:1000,6:500})
    logger.info("Result of move to 150")
    my_robot.check_motor_status(["all"])
    logger.info("Sleep 2")
    time.sleep(10)

    

    my_robot.move_motors_sync2(args={1:0, 2:0, 3:0, 4:0, 5:0, 6:150}, duration={1:1000, 2:500, 3:500, 4:500,5:500,6:500})
    logger.info("Result of move to 150")
    #my_robot.check_motor_status(["all"])
    logger.info("Sleep 2")
    time.sleep(10)
   
    my_robot.check_motor_status(["all"])
    logger.info("Sleep 2")
    my_robot.clean_shutdown()
    logger.info("Ended")

    

def runCalming():
    my_robot = Robot(config_dict=ROBOT_330_LAB)
    my_robot.set_speed(20,200)
    logger.info("Starting positions")
    my_robot.check_motor_status(["all"])
    my_robot.enable_torque()
    my_robot.move_motors_sync(args={1:30, 2:30, 3:30, 4:0}, duration={1:500, 2:500, 3:500, 4:500})
    logger.info("Result of move to 150")
    my_robot.check_motor_status(["all"])
    logger.info("Sleep 2")
    time.sleep(2)
    my_robot.move_motors_sync(args={1:180, 2:180, 3:180, 4:0}, duration={1:500, 2:500, 3:500, 4:500})
    logger.info("Result of move to 150")
    my_robot.check_motor_status(["all"])
    logger.info("Sleep 2")
    time.sleep(2)
    my_robot.check_motor_status(["all"])

    my_robot.clean_shutdown()
    logger.info("Ended")



def runSadness():

    my_robot = Robot(config_dict=ROBOT_330_LAB)
    my_robot.set_speed(2,20)
    logger.info("Starting positions")
    my_robot.check_motor_status(["all"])
    my_robot.enable_torque()

    my_robot.move_motors_sync(args={1:30, 2:30, 3:30, 4:0, 5:90, 6:150}, duration={1:500, 2:500, 3:500, 4:500,5:500,6:500})
    logger.info("Result of move to 150")
    my_robot.check_motor_status(["all"])
    logger.info("Sleep 2")
    time.sleep(2)

    my_robot.set_speed(2,2)
    my_robot.move_motors_sync(args={1:20, 2:30, 3:30, 4:0, 5:70,6:120}, duration={1:500, 2:500, 3:500, 4:500,5:500,6:500})
    logger.info("Result of move to 0")
    my_robot.check_motor_status(["all"])
    logger.info("Sleep 2")
    #time.sleep(2)

    my_robot.set_speed(2,2)
    my_robot.move_motors_sync(args={1:0, 2:20, 3:20, 4:0, 5:50,6:150}, duration={1:500, 2:500, 3:500, 4:500,5:500,6:500})
    logger.info("Result of move to 0")
    my_robot.check_motor_status(["all"])
    logger.info("Sleep 2")
    #time.sleep(2)

    my_robot.set_speed(2,2)
    my_robot.move_motors_sync(args={1:-30, 2:10, 3:10, 4:0, 5:30,6:120}, duration={1:500, 2:500, 3:500, 4:500,5:500,6:500})
    logger.info("Result of move to 0")
    my_robot.check_motor_status(["all"])
    logger.info("Sleep 2")
    #time.sleep(2)

    my_robot.move_motors_sync(args={1:-60, 2:0, 3:0, 4:0, 5:0,6:120}, duration={1:500, 2:500, 3:500, 4:500,5:500,6:500})
    logger.info("Result of move to -150")
    my_robot.check_motor_status(["all"])
    logger.info("Sleep 2")
    #time.sleep(2)
    my_robot.check_motor_status(["all"])

    my_robot.clean_shutdown()
    logger.info("Ended")



def run_happiness():

    my_robot = Robot(config_dict=ROBOT_330_LAB)
    my_robot.set_speed(15,20)
    logger.info("Starting positions")
    my_robot.check_motor_status(["all"])
    my_robot.enable_torque()

    #Always this start setting: 
    my_robot.move_motors_sync(args={1:0, 2:0, 3:0, 4:0, 5:0, 6:150}, duration={1:500, 2:500, 3:500, 4:500,5:500,6:500})
    logger.info("Result of move to 150")
    my_robot.check_motor_status(["all"])
    logger.info("Sleep 2")
    time.sleep(0.5)

    
   
    # Begin happy headshake sequence
    for i in range(2):
        # Tilt head left with slight chin bob
        my_robot.move_motors_sync(args={1: -15, 2: -30, 3: 0, 4: 0, 5: 50, 6: 130},
                                  duration={1: 200, 2: 200, 3: 200, 4: 200, 5: 200, 6: 200})
        logger.info(f"Headshake left {i+1}")
        my_robot.check_motor_status(["all"])
        #time.sleep(0.4)

        # Tilt head right with same chin bob
        my_robot.move_motors_sync(args={1: -15, 2: 0, 3: -30, 4: 0, 5: 50, 6: 130},
                                  duration={1: 200, 2: 200, 3: 200, 4: 200, 5: 200, 6: 200})
        logger.info(f"Headshake right {i+1}")
        my_robot.check_motor_status(["all"])
        #time.sleep(0.4)

        # Final expressive nod (chin down)
        my_robot.move_motors_sync(args={1: 10, 2: 0, 3: 0, 4: 0, 5: 30, 6: 120},
                                duration={1: 300, 2: 300, 3: 300, 4: 300, 5: 300, 6: 300})
        logger.info("Final nod forward")
        my_robot.check_motor_status(["all"])
        #time.sleep(1)
    
    my_robot.move_motors_sync(args={1:0, 2:0, 3:0, 4:0, 5:0, 6:150}, duration={1:500, 2:500, 3:500, 4:500,5:500,6:500})
    logger.info("Result of move to 150")
    my_robot.check_motor_status(["all"])
    logger.info("Sleep 2")
    #time.sleep(2)

    my_robot.clean_shutdown()
    logger.info("Ended")

def run_sadness2():
    my_robot = Robot(config_dict=ROBOT_330_LAB)
    my_robot.set_speed(2, 5)
    logger.info("Starting positions")
    my_robot.check_motor_status(["all"])
    my_robot.enable_torque()

    # Neutral start
    my_robot.move_motors_sync(args={1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 150},
                              duration={1: 500, 2: 500, 3: 500, 4: 500, 5: 500, 6: 500})
    logger.info("Moved to neutral")
    my_robot.check_motor_status(["all"])
    time.sleep(2)

    # Sad gesture: chin down, slight left tilt, hands lowered
    my_robot.move_motors_sync(args={1: -60, 2: -20, 3: -10, 4: 0, 5: 60, 6: 130},
                              duration={1: 800, 2: 800, 3: 800, 4: 800, 5: 800, 6: 800})
    logger.info("Sad head and hands droop")
    my_robot.check_motor_status(["all"])
    time.sleep(2)

    # Small movement to show emotional weight shift
    my_robot.move_motors_sync(args={1: -70, 2: -10, 3: -20, 4: 0, 5: 60, 6: 130},
                              duration={1: 800, 2: 800, 3: 800, 4: 800, 5: 800, 6: 800})
    logger.info("Shifted sadness posture")
    my_robot.check_motor_status(["all"])
    time.sleep(2)

    # Return slowly to neutral
    my_robot.move_motors_sync(args={1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 150},
                              duration={1: 1000, 2: 1000, 3: 1000, 4: 1000, 5: 1000, 6: 1000})
    logger.info("Returning to neutral")
    my_robot.check_motor_status(["all"])
    time.sleep(1)

    my_robot.clean_shutdown()
    logger.info("Sadness gesture ended")


def run_angry():
    my_robot = Robot(config_dict=ROBOT_330_LAB)
    my_robot.set_speed(2, 5)
    logger.info("Starting positions")
    my_robot.check_motor_status(["all"])
    my_robot.enable_torque()

    # Neutral start
    my_robot.move_motors_sync(args={1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 150},
                              duration={1: 500, 2: 500, 3: 500, 4: 500, 5: 500, 6: 500})
    logger.info("Moved to neutral")
    my_robot.check_motor_status(["all"])
    time.sleep(2)

    # Sad gesture: chin down, slight left tilt, hands lowered
    my_robot.move_motors_sync(args={1: -60, 2: -20, 3: -10, 4: 0, 5: 60, 6: 60},
                              duration={1: 800, 2: 800, 3: 800, 4: 800, 5: 800, 6: 800})
    logger.info("Sad head and hands droop")
    my_robot.check_motor_status(["all"])
    time.sleep(2)

    # Small movement to show emotional weight shift
    my_robot.move_motors_sync(args={1: -70, 2: -10, 3: -20, 4: 0, 5: 60, 6: 60},
                              duration={1: 800, 2: 800, 3: 800, 4: 800, 5: 800, 6: 800})
    logger.info("Shifted sadness posture")
    my_robot.check_motor_status(["all"])
    time.sleep(2)

    # Return slowly to neutral
    my_robot.move_motors_sync(args={1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 150},
                              duration={1: 1000, 2: 1000, 3: 1000, 4: 1000, 5: 1000, 6: 1000})
    logger.info("Returning to neutral")
    my_robot.check_motor_status(["all"])
    time.sleep(1)

    my_robot.clean_shutdown()
    logger.info("Sadness gesture ended")

def run_attention():
    my_robot = Robot(config_dict=ROBOT_330_LAB)
    my_robot.set_speed(25, 180)  # Snappy but not too fast
    logger.info("Starting attention gesture")
    my_robot.check_motor_status(["all"])
    my_robot.enable_torque()

    # Initial pose (low posture)
    my_robot.move_motors_sync(args={1: -60, 2: -40, 3: -40, 4: 0, 5: 30, 6: 150},
                              duration={i: 500 for i in range(1, 7)})
    logger.info("Starting from relaxed pose")
    time.sleep(1)

    # Rise to attention: chin up, head straight
    my_robot.move_motors_sync(args={1: -20, 2: 0, 3: 0},
                              duration={1: 600, 2: 600, 3: 600})
    logger.info("Lifted to attentive posture")
    time.sleep(0.7)

   
    my_robot.move_motors_sync(args={5: 90}, duration={5: 400})
    #logger.info(f"Shoulder up {i+1}")
    time.sleep(0.4)

    my_robot.move_motors_sync(args={5: 30}, duration={5: 400})
    #logger.info(f"Shoulder down {i+1}")
    time.sleep(0.4)

    # Hold attentive pose briefly
    time.sleep(1)

    # Return to neutral
    my_robot.move_motors_sync(args={1: 0, 2: 0, 3: 0, 5: 30, 6: 150},
                              duration={i: 500 for i in [1, 2, 3, 5, 6]})
    logger.info("Returning to neutral")
    time.sleep(1)

    my_robot.clean_shutdown()
    logger.info("Attention gesture ended")

def run_gratitude():
    my_robot = Robot(config_dict=ROBOT_330_LAB)
    my_robot.set_speed(15, 12)  # Softer, more graceful motion
    logger.info("Starting gratitude gesture")
    my_robot.check_motor_status(["all"])
    my_robot.enable_torque()

    # Neutral start
    my_robot.move_motors_sync(args={1: 0, 2: 0, 3: 0, 4: 0, 5: 30, 6: 130},
                              duration={i: 500 for i in range(1, 7)})
    logger.info("Moved to neutral")
    my_robot.check_motor_status(["all"])
    time.sleep(1)

    # Gratitude pose: bow head, slight tilt, hands down, head turn
    my_robot.move_motors_sync(args={1: -50, 2: -15, 3: -10, 4: 15, 5: 60, 6: 120},
                              duration={i: 700 for i in range(1, 7)})
    logger.info("Gratitude pose held")
    my_robot.check_motor_status(["all"])
    time.sleep(2)

    # Hold for 1 second, then nod gently once
    my_robot.move_motors_sync(args={1: -60}, duration={1: 400})
    time.sleep(0.4)
    my_robot.move_motors_sync(args={1: -50}, duration={1: 400})
    time.sleep(0.4)

    # Return to neutral slowly
    my_robot.move_motors_sync(args={1: 0, 2: 0, 3: 0, 4: 0, 5: 30, 6: 150},
                              duration={i: 800 for i in range(1, 7)})
    logger.info("Returning to neutral")
    my_robot.check_motor_status(["all"])
    time.sleep(1)

    my_robot.clean_shutdown()
    logger.info("Gratitude gesture ended")

def run_calming():
    my_robot = Robot(config_dict=ROBOT_330_LAB)
    my_robot.set_speed(5, 10)  # Very gentle motion
    logger.info("Starting calming gesture")
    my_robot.check_motor_status(["all"])
    my_robot.enable_torque()

    # Neutral calming starting pose
    my_robot.move_motors_sync(args={1: -20, 2: 0, 3: 0, 4: 0, 5: 30, 6: 150},
                              duration={i: 600 for i in range(1, 7)})
    logger.info("Moved to calming neutral")
    my_robot.check_motor_status(["all"])
    time.sleep(1.5)

    for i in range(2):  # Two cycles of calming motion
        # Head tilt left, shoulder up, arm swings in
        my_robot.move_motors_sync(args={2: -20, 3: 0, 5: 60, 6: 130},
                                  duration={2: 800, 3: 800, 5: 800, 6: 800})
        logger.info(f"Left calming sway {i+1}")
        time.sleep(1.0)

        # Head tilt right, shoulder stays up, arm swings out
        my_robot.move_motors_sync(args={2: 0, 3: -20, 5: 60, 6: 150},
                                  duration={2: 800, 3: 800, 5: 800, 6: 800})
        logger.info(f"Right calming sway {i+1}")
        time.sleep(1.0)

    # Return slowly to calming neutral
    my_robot.move_motors_sync(args={1: -20, 2: 0, 3: 0, 4: 0, 5: 30, 6: 150},
                              duration={i: 800 for i in range(1, 7)})
    logger.info("Returning to calming neutral")
    time.sleep(1.5)

    my_robot.clean_shutdown()
    logger.info("Calming gesture ended")

#def main():
    #run_attention()
    #run_angry()
    #runHappiness()
    #run_sadness2()
    #run_gratitude()
    #runTest()
    #run_calming()
    #return




@app.route('/run', methods=['GET'])
def run_function():
    func_name = request.args.get('emotion')  # Get query parameter
    print(f"Received emotion: {func_name}")  # Debug output

    if func_name == "happiness":
        run_happiness()
    elif func_name == "sadness":
        run_sadness2()
    elif func_name == "calming":
        run_calming()
    elif func_name == "gratitude":
        run_gratitude()
    elif func_name == "attention":
        run_attention()
    else:
        return jsonify({"error": "Unknown function"}), 400

    return jsonify({"status": "success", "executed": func_name})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
    #run_attention()