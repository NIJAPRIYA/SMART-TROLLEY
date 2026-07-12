import common as cm
import cv2
import numpy as np
from PIL import Image
import time
from threading import Thread

import sys
sys.path.insert(0, '/home/pi/opencv_project/myopencv/lib/python3.9/site-packages/human_following')
import util as ut
ut.init_gpio()

cap = cv2.VideoCapture(0)
threshold=0.2
top_k=5 #number of objects to be shown as detected
edgetpu=0
model_dir = '/home/pi/myopencv_project/myopencv/lib/python3.9/site-packages/human_following'
model_file = 'mobilenet_ssd_v2_coco_quant_postprocess.tflite'
lbl = 'coco_labels.txt'

tolerance=0.1
x_deviation=0
y_max=0

object_to_track='person'

#-----initialise motor speed-----------------------------------

import RPi.GPIO as GPIO 
GPIO.setmode(GPIO.BCM)  # choose BCM numbering scheme  
TRIG = 2  # Trigger pin
ECHO = 3  # Echo pin

# Set up GPIO pins
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
# Motor 1 pins
IN1 = 4
IN2 = 17
ENA = 13

# Motor 2 pins
IN3 = 27
IN4 = 22
ENB = 12

# Setup GPIO pins
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)
GPIO.setup(ENB, GPIO.OUT)

# Initialize PWM for speed control
pwmA = GPIO.PWM(ENA, 100)  # Frequency = 100 Hz
pwmB = GPIO.PWM(ENB, 100)

pwmA.start(0)
pwmB.start(0)

def measure_distance():
    # Ensure the trigger pin is LOW
    GPIO.output(TRIG, False)
    time.sleep(0.2)

    # Send a 10µs pulse to TRIG
    GPIO.output(TRIG, True)
    time.sleep(0.00001)  # 10µs
    GPIO.output(TRIG, False)

    # Wait for ECHO pin to go HIGH
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    # Wait for ECHO pin to go LOW
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    # Calculate pulse duration
    pulse_duration = pulse_end - pulse_start

    # Calculate distance in cm
    distance = (pulse_duration * 34300) / 2

    return distance


def set_motor1(direction, speed):
    """
    Controls Motor 1 (connected to IN1, IN2, ENA)
    :param direction: 'forward' or 'backward'
    :param speed: Speed as a percentage (0-100)
    """
    if direction == "forward":
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.HIGH)
    elif direction == "backward":
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
    pwmA.ChangeDutyCycle(speed)

def set_motor2(direction, speed):
    """
    Controls Motor 2 (connected to IN3, IN4, ENB)
    :param direction: 'forward' or 'backward'
    :param speed: Speed as a percentage (0-100)
    """
    if direction == "forward":
        GPIO.output(IN3, GPIO.HIGH)
        GPIO.output(IN4, GPIO.LOW)
    elif direction == "backward":
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.HIGH)
    pwmB.ChangeDutyCycle(speed)


def track_object(objs,labels):
    
    #global delay
    global x_deviation, y_max, tolerance
    
    
    if(len(objs)==0):
        print("no objects to track")
        ut.stop()
        
        return

    flag=0
    for obj in objs:
        lbl=labels.get(obj.id, obj.id)
        if (lbl==object_to_track):
            x_min, y_min, x_max, y_max = list(obj.bbox)
            flag=1
            break
        
    #print(x_min, y_min, x_max, y_max)
    if(flag==0):
        print("selected object no present")
        return
        
    x_diff=x_max-x_min
    y_diff=y_max-y_min
         
    obj_x_center=x_min+(x_diff/2)
    obj_x_center=round(obj_x_center,3)
    
    obj_y_center=y_min+(y_diff/2)
    obj_y_center=round(obj_y_center,3)
    
    x_deviation=round(0.5-obj_x_center,3)
    y_max=round(y_max,3)
        
    print("{",x_deviation,y_max,"}")
   
    thread = Thread(target = move_robot)
    thread.start()
    
def move_robot():
    global x_deviation, y_max, tolerance
    
    y=1-y_max #distance from bottom of the frame
    
    if(abs(x_deviation)<tolerance):
        if(y<0.1):
            
            print("Stopping motors")
            pwmA.ChangeDutyCycle(0)
            pwmB.ChangeDutyCycle(0)
            print("reached person...........")
          
        else:
           
            print("Moving Motor 1 forward at 50% speed")
            set_motor1("forward", 20)
            print("Moving Motor 2 backward at 75% speed")
            set_motor2("backward", 30)
            print("moving robot ...FORWARD....!!!!!!!!!!!!!!")
    
    
    else:
        
        if(x_deviation>=tolerance):
            delay1=get_delay(x_deviation)
                
           # ut.left()
            time.sleep(delay1)
            #ut.stop()
            print("moving robot ...Left....<<<<<<<<<<")
    
                
        if(x_deviation<=-1*tolerance):
            delay1=get_delay(x_deviation)
                
            #ut.right()
            time.sleep(delay1)
            #ut.stop()
            print("moving robot ...Right....>>>>>>>>")
    

    

def get_delay(deviation):
    
    deviation=abs(deviation)
    
    if(deviation>=0.4):
        d=0.080
    elif(deviation>=0.35 and deviation<0.40):
        d=0.060
    elif(deviation>=0.20 and deviation<0.35):
        d=0.050
    else:
        d=0.040
    
    return d

def main():
    print(1)
  
    interpreter, labels =cm.load_model(model_dir, model_file, lbl, edgetpu)
    
    fps=1
   
    while True:
        dist = measure_distance()
        print(f"Distance: {dist:.2f} cm")
        if dist<30:
            print("Stopping motors")
            pwmA.ChangeDutyCycle(0)
            pwmB.ChangeDutyCycle(0)
            
        start_time=time.time()
        
        #----------------Capture Camera Frame-----------------
        ret, frame = cap.read()
        if not ret:
            break
        
        cv2_im = frame
        cv2_im = cv2.flip(cv2_im, 0)
        cv2_im = cv2.flip(cv2_im, 1)

        cv2_im_rgb = cv2.cvtColor(cv2_im, cv2.COLOR_BGR2RGB)
        pil_im = Image.fromarray(cv2_im_rgb)
       
        #-------------------Inference---------------------------------
        cm.set_input(interpreter, pil_im)
        interpreter.invoke()
        objs = cm.get_output(interpreter, score_threshold=threshold, top_k=top_k)
        
        #-----------------other------------------------------------
        track_object(objs,labels)#tracking  <<<<<<<
       
        fps = round(1.0 / (time.time() - start_time),1)
        print("*FPS: ",fps,"**")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
    
