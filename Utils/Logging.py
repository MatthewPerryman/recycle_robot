from time import time, ctime

log_file_name = "log_file_client.txt"

def write_log(write_msg):
	f = open(log_file_name, "a")
	f.write("\n" + write_msg + ": {}".format(ctime(time())))
	f.close()
