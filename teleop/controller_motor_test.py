import RPi.GPIO as GPIO
import evdev
import time

# Pin configuration
AN1_PIN = 18
AN2_PIN = 19
DIG1_PIN = 23
DIG2_PIN = 24

# GPIO setup
# Analog pins determine speed, digital pins determine motor direction
GPIO.setmode(GPIO.BCM)
GPIO.setup(AN1_PIN, GPIO.OUT)
GPIO.setup(AN2_PIN, GPIO.OUT)
GPIO.setup(DIG1_PIN, GPIO.OUT)
GPIO.setup(DIG2_PIN, GPIO.OUT)

# Setup PWM on AN1 and AN2
pwm1 = GPIO.PWM(AN1_PIN, 1000) # 1000Hz freq
pwm2 = GPIO.PWM(AN2_PIN, 1000) # 1000Hz freq
pwm1.start(0)
pwm2.start(0)

# Function to get correct device
def get_controller_event():
  devices = [evdev.InputDevice(path) for path in evdev.list_devices()]

  # Print connected devices
  print('Available devices:')
  for i, device in enumerate(devices):
    print(f'{i}: {device.path} - {device.name}')

  # Check if controller is connected
  for device in devices:
    if 'Xbox Wireless Controller' in device.name:
      return devices
    elif 'Generic X-Box pad' in device.name:
      return device
    
    return None
  
# Function to map joystick input to PWM duty cycle (0, 100)
def joystick_to_pwm(value):
  # Map joystick range (-32000, 32000) to (-50, 50)
  return value / 660

# Set motor direction based on value
def set_motor_direction(axis_value, dig_pin):
  if axis_value >= 0:
    GPIO.output(dig_pin, GPIO.HIGH)
  else:
    GPIO.output(dig_pin, GPIO.LOW)

# Initialize controller
controller = get_controller_event()

while controller == None:
  print('Controller not found, please check devices')
  print('Waiting 5 seconds...')
  time.sleep(5)