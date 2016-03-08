#!/usr/bin/python
import os,sys,socket
import thread
import select
import time
import signal
import Queue

shell_exit = 0
g_queue = None

def signal_ctrlc_Handler(signal, frame):
	global g_queue
	print "Received Ctrl+C"
	if g_queue == None:
		print "No Queue yet."
		sys.exit(0)
	g_queue.put("\x03")

def redirect_output(s):
	global shell_exit
	while 1:
		a = s.recv(128)
		if len(a) == 0:
			print "Socket is closed."
			break

		if a.find("Script done, file is /dev/null") != -1:
			print "shell is done."
			shell_exit = 1
			break

		for b in a:
			sys.stdout.write(b)
		sys.stdout.flush()

		time.sleep(0.01)

def runshell(s, shell = "/bin/sh"):
	global shell_exit
	global g_queue
	g_queue = Queue.Queue()
	signal.signal(signal.SIGINT, signal_ctrlc_Handler)
	print "Welcome to the shell world. Enjoy your shell.."
	print "----------------------------------------------"
	try:
		thread.start_new_thread(redirect_output, (s,))
	except Exception as e:
		print "Error: thread start failed:%s " % e
		return

	#read prompt ps
	a = "script -c \"%s\" /dev/null" % shell
	s.send(a + "\n")
	#s.send("stty intr ^C\n")
	timeout = 0.1
	two_ctrlc = 0;
	while 1:
		try:
			#print "receiving queue"
			item = g_queue.get(False)
			two_ctrlc = two_ctrlc + 1
			if two_ctrlc == 2:
				print "Two sigint. quit."
				s.send("exit\n")
			if two_ctrlc == 3:
				print "Three sigint. exit."
				break
		except Queue.Empty:
			#print "no job in queue"
			f = 1
		except Exception as e:
			print "read queue failed:%s" % e
			break
		if shell_exit == 1:
			s.send("exit\n")
			break
		readlist = None
		try:
			readlist, _, _ = select.select([sys.stdin], [], [], timeout)
		except select.error as select_Error:
			if select_Error[0] == 4:
				continue
			else:
				print select_Error	
				raise
		if readlist:
			two_ctrlc = 0
			a = sys.stdin.readline()
			s.send(a)
		#else:
			#print "timeout, read again"

if __name__ == "__main__":
	s = None
	host = "127.0.0.1"
	port = 5400
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print "Connecting to %s:%d" % (host, port)
		s.connect((host, port))
	except Exception as e:
		print "ERROR: %s" % e
		s.close()
		sys.exit(0)

	if s == None:
		sys.exit(0)

	runshell(s, "bash")
#
