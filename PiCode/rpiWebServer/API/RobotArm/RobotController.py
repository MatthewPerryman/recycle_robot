from uarm.wrapper import SwiftAPI


class RobotController:
	swift = None

	def start_transmission(self):
		self.swift.flush_cmd(wait_stop=True)
		self.swift.waiting_ready(timeout=3)

	## Clear cmd buffer and close connection
	def end_transmission(self):
		self.swift.flush_cmd(wait_stop=True)
		self.swift.waiting_ready(timeout=3)

	## Move the robot arm by an increment value
	def move_by_vector(self, vector, reverse_vector=False, speed=100000):
		self.start_transmission()

		# Calculate new position and send update
		# TODO: Create vector class
		old = self.swift.get_position()

		if reverse_vector:
			new_location = [old[0] - vector[0], old[1] - vector[1], old[2] - vector[2]]
		else:
			new_location = [old[0] + vector[0], old[1] + vector[1], old[2] + vector[2]]

		self.move_to(new_location)
		
		self.end_transmission()

		return old, new_location

	## Move the robot arm to this vector
	# TODO: Return boolean of success
	def move_to(self, new_location, speed=100000):
		self.start_transmission()

		self.swift.set_position(x=new_location[0], y=new_location[1], z=new_location[2])

		self.end_transmission()
		return new_location

	## Create the API context and put robot on standby
	def __init__(self):
		if self.swift == None:
			self.swift = SwiftAPI()
			self.swift.waiting_ready(timeout=3)

		self.swift.flush_cmd(wait_stop=True)

		# Reset the arms location
		self.swift.reset()
		self.swift.waiting_ready(timeout=3)

		self.end_transmission()

	def __del__(self):
		self.swift.flush_cmd(wait_stop=True)
		self.swift.disconnect()
