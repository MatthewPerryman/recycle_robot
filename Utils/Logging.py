from time import time

log_file_name = "log_file.txt"

def write_log(write_msg):
	f = open(log_file_name, "a")
	f.write("\n" + write_msg + ": {}".format(time()))
	f.close()