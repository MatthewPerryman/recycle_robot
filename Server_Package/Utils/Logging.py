from time import time, ctime

log_file_name = "log_file_server.txt"


def write_log(write_msg):
	f = open(log_file_name, "a")
	f.write("\n" + "{}: ".format(ctime(time()) + write_msg))
	f.close()
