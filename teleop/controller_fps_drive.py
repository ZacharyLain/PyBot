from gpiozero import LED, PWMLED
import evdev
from time import sleep

# Define GPIO pins for the motors
AN1_PIN = 18  # GPIO pin for motor 1 PWM
AN2_PIN = 19  # GPIO pin for motor 2 PWM
DIG1_PIN = 23  # GPIO pin for motor 1 direction
DIG2_PIN = 24  # GPIO pin for motor 2 direction

AN1 = PWMLED(AN1_PIN)
AN2 = PWMLED(AN2_PIN)
DIG1 = LED(DIG1_PIN)
DIG2 = LED(DIG2_PIN)

# Function to get the correct controller device
def get_controller_event():
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]

    print('Available devices:')
    for i, device in enumerate(devices):
        print(f'{i}: {device.path} - {device.name}')

    for device in devices:
        if 'Xbox Wireless Controller' in device.name or 'Generic X-Box pad' in device.name:
            return device

    return None

# Function to initialize the controller and reconnect if necessary
def initialize_controller():
    controller = get_controller_event()

    while controller is None:
        print('Controller not found, please check devices')
        print('Waiting 5 seconds...')
        sleep(5)
        controller = get_controller_event()

    print(f'Controller connected: {controller.name}')
    return controller

# gpiozero PWM is on a scale of (0,1), our joystick values are from ~(-33000, 33000)
def joystick_to_pwm(value):
  # max value (33000) will be mapped to a little under 1
  return value / 40000

# Motor controller requires an on/off dig signal to determine motor directions
def set_motor_direction(direction, dig_pin):
    if direction == 1:
      dig_pin.on()
    else:
      dig_pin.off()
      
def move_motor(value, pwm_pin, dig_pin):
  if value >= 0:
    direction = 1
  else:
    direction = 0
    value *= -1

  # Add deadzone, controllers are sensitive
  if value <= 1500:
    value = 0
  
  # print(f'Pin: {pwm_pin}\tValue: {value}\tDirection: {direction}')

  # Set motor speed and direction
  pwm_pin.value = joystick_to_pwm(value)
  set_motor_direction(direction, dig_pin)

# Main loop to read controller events with reconnection handling
controller = initialize_controller()

try:
    for event in controller.read_loop():
        if event.type == evdev.ecodes.EV_ABS:
            absevent = evdev.categorize(event)
            axis = absevent.event.code
            value = absevent.event.value
            left_value = 0
            right_value = 0

            # Adjust value for Bluetooth controller if necessary
            if controller.name == 'Xbox Wireless Controller':
              value -= 32000
            
            # Right stick controls right wheel
            if axis == evdev.ecodes.ABS_RX: # this needs double checked
              left_value -= value
              right_value += value
              
              
            # Left stick controls left wheel
            if axis == evdev.ecodes.ABS_Y:
              left_value += value
              right_value += value

            move_motor(left_value, AN1, DIG1)
            move_motor(right_value, AN2, DIG2)



except (OSError, IOError) as e:
    # Handle disconnection and attempt to reconnect
    print("Controller disconnected. Attempting to reconnect...")
    controller.close()
    controller = initialize_controller()

except KeyboardInterrupt:
    print("Exiting program...")