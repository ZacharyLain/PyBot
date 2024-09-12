import gpiod
import evdev
import time

# Define GPIO pins for the motors
AN1_PIN = 18  # GPIO pin for motor 1 PWM
AN2_PIN = 19  # GPIO pin for motor 2 PWM
DIG1_PIN = 23  # GPIO pin for motor 1 direction
DIG2_PIN = 24  # GPIO pin for motor 2 direction

# Set up GPIO chip and lines
chip = gpiod.Chip('gpiochip0')
an1_line = chip.get_line(AN1_PIN)
an2_line = chip.get_line(AN2_PIN)
dig1_line = chip.get_line(DIG1_PIN)
dig2_line = chip.get_line(DIG2_PIN)

# Request lines as outputs
an1_line.request(consumer='pwm1', type=gpiod.LINE_REQ_DIR_OUT)
an2_line.request(consumer='pwm2', type=gpiod.LINE_REQ_DIR_OUT)
dig1_line.request(consumer='dir1', type=gpiod.LINE_REQ_DIR_OUT)
dig2_line.request(consumer='dir2', type=gpiod.LINE_REQ_DIR_OUT)

# Function to set the PWM duty cycle using software PWM
def set_pwm(line, duty_cycle):
    """
    Sets the duty cycle for a line using software PWM.
    :param line: gpiod line object.
    :param duty_cycle: Duty cycle (0 to 1).
    """
    period = 0.02  # 20ms period for the PWM signal
    on_time = duty_cycle * period
    off_time = period - on_time

    if duty_cycle > 0:
        line.set_value(1)
        time.sleep(on_time)
    line.set_value(0)
    time.sleep(off_time)

# Function to set motor direction
def set_motor_direction(direction, line):
    """
    Sets the direction of the motor.
    :param direction: 1 for forward, -1 for reverse.
    :param line: gpiod line object for the direction pin.
    """
    line.set_value(1 if direction > 0 else 0)

# Function to map joystick input to PWM duty cycle (0, 1)
def joystick_to_pwm(value):
    return max(0, min(value / 66000, 1))  # Convert joystick range to 0-1

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

# Move motor based on joystick input
def move_motor(pwm_line, direction_line, value):
    direction = 1 if value >= 0 else -1
    abs_value = abs(value)

    # Apply deadzone threshold to avoid motor movement on small joystick deviations
    if abs_value < 1500:
        abs_value = 0

    pwm_value = joystick_to_pwm(abs_value)
    pwm_line.ChangeDutyCycle(pwm_value)  # Set PWM duty cycle (0 to 1)

    print(f'pwm_line: {pwm_line}\tpwm_value: {pwm_value}')

    set_motor_direction(direction, direction_line)

# Function to initialize the controller and reconnect if necessary
def initialize_controller():
    controller = get_controller_event()

    while controller is None:
        print('Controller not found, please check devices')
        print('Waiting 5 seconds...')
        time.sleep(5)
        controller = get_controller_event()

    print(f'Controller connected: {controller.name}')
    return controller

# Main loop to read controller events with reconnection handling
controller = initialize_controller()

try:
    for event in controller.read_loop():
        if event.type == evdev.ecodes.EV_ABS:
            absevent = evdev.categorize(event)
            axis = absevent.event.code
            value = absevent.event.value

            # Adjust value for Bluetooth controller if necessary
            if controller.name == 'Xbox Wireless Controller':
                value -= 32000

            # Left stick controls left wheel
            if axis == evdev.ecodes.ABS_Y:
                # print(f'an1_line: {an1_line}\tdig1_line: {dig1_line}\tvalue: {value}')
                move_motor(an1_line, dig1_line, value)
                last_left_value = value

            # Right stick controls right wheel
            if axis == evdev.ecodes.ABS_RZ:
                # print(f'an2_line: {an2_line}\tdig2_line: {dig2_line}\tvalue: {value}')
                move_motor(an2_line, dig2_line, value)
                last_right_value = value


except (OSError, IOError) as e:
    # Handle disconnection and attempt to reconnect
    print("Controller disconnected. Attempting to reconnect...")
    controller.close()
    controller = initialize_controller()

except KeyboardInterrupt:
    print("Exiting program...")

finally:
    # Release GPIO lines
    an1_line.release()
    an2_line.release()
    dig1_line.release()
    dig2_line.release()
