import evdev
import time

# List connected devices
devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
for device in devices:
  print(device.path, device.name)

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

# Initialize controller
controller = get_controller_event()

while controller == None:
  print('Controller not found, please check devices')
  print('Waiting 5 seconds...')
  time.sleep(5)

# Read controller events
for event in controller.read_loop():
  if event.type == evdev.ecodes.EV_ABS:
    absevent = evdev.categorize(event)
    axis = absevent.event.code
    value = absevent.event.value

    print(f'Axis: {axis}, Value: {(value - 32000) * -1}')