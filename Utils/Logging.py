from time import time, ctime

log_name = "log_file_"
log_extension = ".log"


def write_log(writer, write_msg):
	if writer == "client" or writer == "server":
		f = open(log_name + writer + log_extension, "a")
		f.write("\n" + "{}: {}".format(ctime(time()), write_msg))
		f.close()
	else:
		print("Please state: client or server")
