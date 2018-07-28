'''
Daemon Thread Classes
This code was obtained from: http://web.archive.org/web/20131025230048/http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
'''

import sys, os, time, atexit, signal


class DaemonBase:

	def __init__(self, pidfile, workpath='/'):

		self.pidfile = pidfile
		self.workpath = workpath

	def perror(self, msg, err):

		msg = msg + '\n'
		sys.stderr.write(msg.format(err))
		sys.exit(1)

	def daemonize(self):
		"""Daemonize class process. (UNIX double fork mechanism).
		"""
		if not os.path.isdir(self.workpath):
			self.perror('workpath does not exist!', '')

		try: # exit first parent process
			pid = os.fork()
			if pid > 0: sys.exit(0)
		except OSError as err:
			self.perror('fork #1 failed: {0}', err)

		# decouple from parent environment
		try: os.chdir(self.workpath)
		except OSError as err:
			self.perror('path change failed: {0}', err)

		os.setsid()
		os.umask(0)

		try: # exit from second parent
			pid = os.fork()
			if pid > 0: sys.exit(0)
		except OSError as err:
			self.perror('fork #2 failed: {0}', err)

		# redirect standard file descriptors
		sys.stdout.flush()
		sys.stderr.flush()
		si = open(os.devnull, 'r')
		so = open(os.devnull, 'a+')
		se = open(os.devnull, 'a+')
		os.dup2(si.fileno(), sys.stdin.fileno())
		os.dup2(so.fileno(), sys.stdout.fileno())
		os.dup2(se.fileno(), sys.stderr.fileno())

		# write pidfile
		atexit.register(os.remove, self.pidfile)
		pid = str(os.getpid())
		with open(self.pidfile,'w+') as f:
			f.write(pid + '\n')
		self.run()

	def run(self):
		""" This method needs to be overridden with the program that needs to run on the daemon thread
		"""
		while True:
			time.sleep(1)



class DaemonControl:

	def __init__(self, daemon, pidfile, workdir='/'):
		
		self.daemon = daemon
		self.pidfile = pidfile
		self.workdir = workdir


	def start(self):
		"""Start the daemon.
		"""
		try: # check for pidfile to see if the daemon already runs
			with open(self.pidfile, 'r') as pf:
				pid = int(pf.read().strip())
		except IOError: pid = None

		if pid:
			message = "pidfile {0} already exist. " + \
					"Daemon already running?\n"
			sys.stderr.write(message.format(self.pidfile))
			sys.exit(1)

		# Start the daemon
		d = self.daemon(self.pidfile, self.workdir)
		d.daemonize()

	def stop(self):
		"""Stop the daemon.

		This is purely based on the pidfile / process control
		and does not reference the daemon class directly.
		"""
		try: # get the pid from the pidfile
			with open(self.pidfile,'r') as pf:
				pid = int(pf.read().strip())
		except IOError: pid = None

		if not pid:
			message = "pidfile {0} does not exist. " + \
					"Daemon not running?\n"
			sys.stderr.write(message.format(self.pidfile))
			return # not an error in a restart

		try: # try killing the daemon process
			while 1:
				os.kill(pid, signal.SIGTERM)
				time.sleep(0.1)
		except OSError as err:
			e = str(err.args)
			if e.find("No such process") > 0:
				if os.path.exists(self.pidfile):
					os.remove(self.pidfile)
			else:
				print (str(err.args))
				sys.exit(1)

	def restart(self):
		"""Restart the daemon.
		"""
		self.stop()
		self.start()
