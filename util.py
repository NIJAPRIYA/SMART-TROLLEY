import RPi.GPIO as GPIO
GPIO.setwarnings(False)

import os, time

edgetpu=0 # If Coral USB Accelerator connected, then make it '1' otherwise '0'

m1_1 = 8
m1_2 = 11
m2_1 = 14 
m2_2 = 15 
TRIG_PIN = 23
ECHO_PIN = 24


def init_gpio():
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(m1_1,GPIO.OUT)
	GPIO.setup(m1_2,GPIO.OUT)
	GPIO.setup(m2_1,GPIO.OUT)
	GPIO.setup(m2_2,GPIO.OUT)
	
	GPIO.setup(TRIG_PIN, GPIO.OUT)
	GPIO.setup(ECHO_PIN, GPIO.OUT)
	

def back():
    print("moving back!!!!!!")
    GPIO.output(m1_1, False)
    GPIO.output(m1_2, True)
    GPIO.output(m2_1, True)
    GPIO.output(m2_2, False)
    
def right():
	GPIO.output(m1_1, True)
	GPIO.output(m1_2, False)
	GPIO.output(m2_1, True)
	GPIO.output(m2_2, False)

def left():
	GPIO.output(m1_1, False)
	GPIO.output(m1_2, True)
	GPIO.output(m2_1, False)
	GPIO.output(m2_2, True)
	
def forward():
	GPIO.output(m1_1, True)
	GPIO.output(m1_2, False)
	GPIO.output(m2_1, False)
	GPIO.output(m2_2, True)
	
def stop():
	GPIO.output(m1_1, False)
	GPIO.output(m1_2, False)
	GPIO.output(m2_1, False)
	GPIO.output(m2_2, False)

def speak_tts(text,gender):
	cmd="python /var/www/html/earthrover/speaker/speaker_tts.py '" + text + "' " + gender + " &"
	os.system(cmd)
	
def get_distance():
    # Trigger the sensor
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)  # 10 microseconds pulse
    GPIO.output(TRIG_PIN, False)

    # Measure the pulse duration
    while GPIO.input(ECHO_PIN) == 0:
        pulse_start = time.time()
    
    while GPIO.input(ECHO_PIN) == 1:
        pulse_end = time.time()
    
    pulse_duration = pulse_end - pulse_start

    # Calculate distance (speed of sound is ~34300 cm/s)
    distance = pulse_duration * 17150  # in cm
    distance = round(distance, 2)
    return distance
