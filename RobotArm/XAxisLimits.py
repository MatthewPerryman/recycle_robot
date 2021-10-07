from uarm.wrapper import SwiftAPI
import time

swift = SwiftAPI()


swift.waiting_ready()
swift.flush_cmd()

swift.connect()


swift.reset(wait=True, speed=100000)
swift.set_position(x=110, z=50, wait=True, speed=100000)


location = swift.get_position()

print("Arm Position: ", location)
cmd_success = True
increment = 1

while cmd_success:
    location[0] += increment

    swift.set_position(x=location[0], wait=True, speed=10000)
    print("Arm Position: ", swift.get_position())

    #time

    if int(swift.get_position()[0]) == int(location[0]-1):
        print("Arm Position (Direction Change): ", swift.get_position())
        increment = -1

swift.flush_cmd(wait_stop=True)

swift.disconnect()


