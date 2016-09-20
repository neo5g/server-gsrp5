import sys
import os
import selectors
import errno
import socket
import select
import signal
import traceback
import logging
import ssl
import time
import threading
from socketserver import _ServerSelector
import selectors
from logging.handlers import RotatingFileHandler
from multiprocessing import Process,Queue,freeze_support, cpu_count, active_children

from os.path import join as opj
from tools.translations import trlocal as _
from tools.packer import Packer
from modules.loading import add_module_paths

import managers
from dispatcher.dispatcher import Dispatcher

add_module_paths(os.getcwd(),{'basic':None,'addons':None})

__list_sockets__ = {}
__list_processes__ = {}
_is_shutdown = False

if not "EPOLLRDHUP" in dir(select):
	select.EPOLLRDHUP = 0x2000

_logger = logging.getLogger("listener."+__name__)

epoll = _ServerSelector()

class Server(object):
	_BaseServer_shutdown_request = False

def stop(signum,stack):
	global __list_sockets__
	global __list_processes__
	ths = threading.enumerate()
	for th in ths:
		if th.getName() != "MainThread":
			inq.put(None)
	for key in __list_sockets__.keys():
		__list_sockets__[key]['socket'].close()
	for key in __list_processes__.keys():
		__list_processes__[key].terminate()
	__list_sockets__ = {}
	__list_processes__ = {}
	os._exit(0)


def child(signum,stack):
	global __list_processes__
	pid,status = os.wait()
	if pid in __list_processes__:
		print('PID,STATUS:',pid,status)
		del __list_processes__[pid]
	return False

signal.signal(signal.SIGTERM, stop)
signal.signal(signal.SIGINT, stop)
signal.signal(signal.SIGQUIT, stop)
signal.signal(signal.SIGCHLD, child)


inq = Queue()
pinq = Queue()
outq = Queue()

#lock = threading.Lock()


# Start of new handlers

def inqHandle(inq,pinq):
	while True:		
		km = inq.get()
		if km is None:
			break
		#lock.acquire()
		key,mask = km
		print("key.fd in __list_sockets__",key.fd,key.fd in __list_sockets__,key)
		if not key.fd in __list_sockets__:
			#lock.release()
			continue
		server = __list_sockets__[key.fd]['server']
		print("server",server)
		msg = server.packer._readfromfp(server, server.rfile)
		if len(msg) == 0:
			print("close:",key.fd)
			server.rfile.close()
			server.wfile.flush()
			server.wfile.close()
			obj = __list_sockets__[key.fileobj]
			obj['socket'].close()
			epoll.unregister(key.fd)
			_logger.info('Connection closed host %s port %s' % (obj['info'][0],obj['info'][1]))
			if key.fd in __list_sockets__:
				del __list_sockets__[key.fd]
				print("unregister:\n",key.fd,'\n',__list_sockets__,'\n')
			#lock.release()
			continue

		imsg = [key.fd]
		imsg.extend(msg)	
		pinq.put(imsg)
		e=epoll.register(__list_sockets__[key.fd]['socket'],selectors.EVENT_READ,key.data)
		print("EEEE:",e)
		#lock.release()

def outqHandle(poutq):

	while True:
		msg = poutq.get()
		if msg is None:
			break
		chan = msg[0]
		rmsg = msg[1:]
		print("CHAN",chan,rmsg)
		server = __list_sockets__[chan]['server']
		server.packer._writetofp(rmsg, server.wfile)
		

def pinqHandle(pinq,outq):
	dispatcher = Dispatcher(managers.manager.MetaManager.__list_managers__,os.getcwd())
	while True:
		msg = pinq.get()
		if msg is None:
			break
		try:
			chan = msg[0]
			imsg = msg[1:]
			rmsg = [chan]
			_logger.info('IMessage: %s' % (imsg,))
			if imsg and len(imsg) == 1:
				rmsg.extend(dispatcher._execute(imsg[0]))
			elif imsg and len(imsg) == 2:
				rmsg.extend(dispatcher._execute(imsg[0],imsg[1]))
			_logger.info('RMessage: %s' % (rmsg,))
			outq.put(rmsg) 
		except:
			e = traceback.format_exc()
			_logger.critical(e)
			outq.put(rmsg.extend(['E', e]))

def qhandle(key,mask):
	#print('qhandle',key,mask)
	epoll.unregister(key.fileobj)
	inq.put([key,mask])

		
def accept(key,mask):
	conn, addr = __list_sockets__[key.fd]['socket'].accept()
	conn.setblocking(True)
	conn.settimeout(900)
	conn.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,True)
	server = Server()
	server.packer = Packer()
	server.rfile = conn.makefile(mode='rb', buffering = -1)
	server.wfile = conn.makefile(mode='wb', buffering = 0)
	ci = conn.getsockname()
	key = epoll.register(conn,selectors.EVENT_READ,qhandle)
	print("KEY:",key)
	__list_sockets__[key.fd] = {'socket':conn,'server':server,'address':addr,'info':ci}
	_logger.info(_("Connect on host %s port %s") % (ci[0],ci[1]))

def main():
	__list_servicies__ = {'tcprpc':{'address_family':socket.AF_INET,'socket_type':socket.SOCK_STREAM,'allow_reuse_address':False},'tcpv6rpc':{'address_family':socket.AF_INET6,'socket_type':socket.SOCK_STREAM,'allow_reuse_address':False}}
	pwd = os.getcwd()
	CONFIG_PATH= opj(pwd,'conf')
	CONFIG_FILE = opj(pwd,'conf/gsrp-listener.conf')
	LOGGING_FILE = opj(pwd,'listener.log')	
	SIDS_PATH = opj(pwd,'sids/sids.conf')
	from optparse import OptionParser
	from tools.config import configManager
	parser = OptionParser(version = '1.0', description = _('Listener of global system resource planned'))
	parser.add_option('-c','--config',type='string', dest = 'config_file',help ='Config file', default = CONFIG_FILE)
	parser.add_option('-l','--logfile',type='string', dest = 'log_file',help ='Logging file', default = LOGGING_FILE)
	parser.add_option('-s','--sidspath',type='string', dest = 'sids_path',help ='Sids path', default = SIDS_PATH)
	options,arguments=parser.parse_args()
	if 'config_path'in  options.__dict__:
		if options.__dict__['config_path'] != CONFIG_PATH:
			CONFIG_PATH = options.__dict__['config_path']
	if 'sid_path' in options.__dict__:
		if options.__dict__['sids_path'] != SIDS_PATH:
			SIDS_PATH = options.__dict__['sids_path']
	config = configManager(CONFIG_FILE)
	formatter = logging.Formatter(fmt = "%(asctime)s - %(name)s - %(levelname)s: -%(filename)s: %(module)s: - %(exc_info)s - процесс:%(process)d: - нить:%(thread)s: - %(threadName)s: - %(message)s")
	streamhandler = logging.StreamHandler()
	rotatingfilehandler = RotatingFileHandler('listener.log', maxBytes = 1024*1024, backupCount = 9, encoding = 'UTF-8')
	streamhandler.setFormatter(formatter)
	rotatingfilehandler.setFormatter(formatter)
	_logger.setLevel(logging.INFO)
	_logger.addHandler(streamhandler)
	_logger.addHandler(rotatingfilehandler)

	for key in config['globals'].keys():
		if key in ('tcprpc','tcpv6rpc') and config['globals'][key]:
			s=socket.socket(__list_servicies__[key]['address_family'],__list_servicies__[key]['socket_type'])
			if __list_servicies__[key]['allow_reuse_address']:
				s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
			s.bind((config[key]['host'],config[key]['port']))
			s.listen(5)
			__list_sockets__[s.fileno()] = {'socket':s,'service':key}
			s.setblocking(False)
			reg =  epoll.register(s,selectors.EVENT_READ,accept)
			print("reg",reg)
			__list_sockets__[reg.fd] = {'socket':s,'service':key}
			_logger.info(_("service %s running on %s port %s") % (key, config[key]['host'], config[key]['port'])) 

	if __list_sockets__.keys().__len__() > 0:
		for i in range(cpu_count()*2):
			tin = threading.Thread(group=None,target=inqHandle,name='inqhandle- %03s' % i,args=(inq,pinq),daemon=False)
			tin.start()
			tout = threading.Thread(group=None,target=outqHandle,name='outqhandle- %03s' % i,args=(outq,),daemon=False)
			tout.start()
			p = Process(group=None,target=pinqHandle,name="worker-%s" % (i,),args=(pinq,outq),kwargs={},daemon=None)
			p.start()

		while not _is_shutdown:
			events = epoll.select()
			for key, mask in events:
				if key.fd in __list_sockets__:
					callback = key.data
					callback(key,mask)
				else:
					epoll.unregister(key.fd)
	else:
		_logger.info(_("Enable services not defined")) 


if __name__ == "__main__":
	main()
