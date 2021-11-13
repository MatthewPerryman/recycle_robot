from uarm.wrapper import SwiftAPI
import time

swift = SwiftAPI()

swift.waiting_ready()
swift.flush_cmd()

swift.connect()

print("Pump Status: ", swift.get_pump_status())

print("Arm Position: ", swift.get_position())

swift.reset(wait=True, speed=100000)

# Forward
swift.set_position(x=200, y=200, z=100, speed=100000, wait=True)
swift.set_position(x=200, y=200, z=0, speed=100000, wait=True)
time.sleep(1)
swift.set_pump(True)

swift.set_position(x=200, y=-200, z=100, speed=100000, wait=True)
swift.set_position(x=200, y=-200, z=0, speed=100000, wait=True)
time.sleep(1)
swift.set_pump(False)

swift.reset()

# Reverse
swift.set_position(x=200, y=-200, z=100, speed=100000, wait=True)
swift.set_position(x=200, y=-200, z=0, speed=100000, wait=True)
time.sleep(1)
swift.set_pump(True)

swift.set_position(x=200, y=200, z=100, speed=100000, wait=True)
swift.set_position(x=200, y=200, z=0, speed=100000, wait=True)
time.sleep(1)
swift.set_pump(False)

swift.reset(wait=True, speed=100000)

swift.flush_cmd(wait_stop=True)

print("Arm Position: ", swift.get_position())

swift.disconnect()
