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
      return device
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

def move_motor(pwm, dig_pin):
  if value >= 0:
    direction = 1
  else:
    direction = -1
    value *= -1

  # Add in a deadzone, these controllers are sensitive
  if value < 1500:
    value = 0

  # Set motor speed
  pwm_value = joystick_to_pwm(value)
  pwm.ChangeDutyCycle(pwm_value)
  set_motor_direction(direction, dig_pin)

# Initialize controller
controller = get_controller_event()

while controller == None:
  print('Controller not found, please check devices')
  print('Waiting 5 seconds...')
  time.sleep(5)

# Main loop
# Read controller events
for event in controller.read_loop():
  if event.type == evdev.ecodes.EV_ABS:
    absevent = evdev.categorize(event)
    axis = absevent.event.code
    value = absevent.event.value

    # Normalize the value if controller is connected via Bluetooth
    # For some reason if the controller is wired in it is -32000=>32000
    # But when connected through Bluetooth it is 0=>64000
    if (controller.name == 'Xbox Wireless Controller'):
      value -= 33000 # rounded up because if the PWM value is out of (0, 100) range it throws an error

    # Left stick controls left wheel
    if axis == evdev.ecodes.ABS_Y:
      move_motor(pwm1, DIG1_PIN)

      # Right stick controls right wheel
    if axis == evdev.ecodes.ABS_RZ:
      move_motor(pwm2, DIG2_PIN)

# Close program
pwm1.stop()
pwm2.stop()
GPIO.cleanup()