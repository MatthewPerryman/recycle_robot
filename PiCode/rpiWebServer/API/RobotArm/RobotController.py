from uarm.wrapper import SwiftAPI

class RobotController:

	## Clear cmd buffer and close connection
	def end_transmission(self):
		self.swift.flush_cmd(wait_stop=True)
		
	## Move the robot arm by an increment value
	def move_by_increment(self, update_vector, speed=100000):
		
		# Calculate new position and send update
		# TODO: Create vector class
		location = self.swift.get_position()
		new_location = [location[0] + update_vector[0], location[1] + update_vector[1], location[2] + update_vector[2]]
		self.swift.set_position(new_location[0], new_location[1], new_location[2])
		
	## Move the robot arm to this vector
	def move_to(self, relative_vector, speed=100000):
		location = self.swift.get_position()
		new_location = location[0] + int(relative_vector[0]), location[1] + int(relative_vector[1]), location[2] + int(relative_vector[2])
		self.swift.set_position(x=new_location[0], y=new_location[1], z=new_location[2])
		return location, new_location
		
	## Create the API context and put robot on standby
	def __init__(self):
		self.swift = SwiftAPI()
		self.swift.flush_cmd(wait_stop=True)
		
		# Reset the arms location	
		self.swift.connect()
		self.swift.reset()
		self.swift.waiting_ready()
		
		self.end_transmission()
		
	def __del__(self):
		self.swift.flush_cmd(wait_stop=True)
		self.swift.disconnect()
