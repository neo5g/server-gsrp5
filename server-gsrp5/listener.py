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
from socketserver import _ServerSelector
import selectors
from logging.handlers import RotatingFileHandler
from multiprocessing import Process, Pool, freeze_support, cpu_count, active_children

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

def whandle(umsg):
	server = managers._server
	try:
		_logger.info('IMessage: %s' % (umsg,))
		if umsg and len(umsg) == 1:
			rmsg = server._dispatcher._execute(umsg[0])
		elif umsg and len(umsg) == 2:
			rmsg = server._dispatcher._execute(umsg[0],umsg[1])
		_logger.info('RMessage: %s' % (rmsg,))
		return rmsg
	except:
		e = traceback.format_exc()
		_logger.critical(e)
		print('TRACEBACK',e)
		return ['E', e]


def phandle(key,mask):
	process = Process(target=handle,name='handle- %s' % key.fd,args=(key.fd,mask),daemon=True)
	process.start()


def handle(key, mask):
	try:
		obj = __list_sockets__[key.fd]
		server = obj['server']
		umsg = server.packer._readfromfp(server, server.rfile)
		if len(umsg) == 0:
			server.rfile.close()
			server.wfile.close()
			obj['socket'].close()
			epoll.unregister(key.fd)
			del __list_sockets__[key.fd]
			_logger.info('Connection closed host %s port %s' % (obj['info'][0],obj['info'][1]))
			return
			
		res = pool.apply_async(func = whandle,args=(umsg,),callback=None) 
		rmsg = res.get(timeout=900)
		server.packer._writetofp(rmsg, server.wfile)
	except:
		_logger.critical(traceback.format_exc())
		print('TRACEBACK',traceback.format_exc())
		server.packer._writetofp(['E', traceback.format_exc()],server.wfile)

def initializer():
	from tools.packer import Packer
	from modules.loading import add_module_paths
	import managers
	from dispatcher.dispatcher import Dispatcher
	add_module_paths(os.getcwd(),{'basic':None,'addons':None})
	server = Server()
	server._dispatcher = Dispatcher(managers.manager.MetaManager.__list_managers__,os.getcwd())
	server.packer = Packer()
	managers._server = server


def accept(key,mask):
	conn, addr = __list_sockets__[key.fd]['socket'].accept()
	conn.setblocking(False)
	server = Server()
	server.packer = Packer()
	server.rfile = conn.makefile(mode='rb', buffering = -1)
	server.wfile = conn.makefile(mode='wb', buffering = 0)
	ci = conn.getsockname()
	__list_sockets__[conn.fileno()] = {'socket':conn,'server':server,'address':addr,'info':ci}
	epoll.register(conn.fileno(),selectors.EVENT_READ,handle)
	_logger.info(_("Connect on host %s port %s") % (ci[0],ci[1]))

pool = Pool(initializer=initializer)

def main():
	__list_servicies__ = {'tcprpc':{'address_family':socket.AF_INET,'socket_type':socket.SOCK_STREAM,'allow_reuse_address':False,'handler':handle},'tcpv6rpc':{'address_family':socket.AF_INET6,'socket_type':socket.SOCK_STREAM,'allow_reuse_address':False,'handler':handle}}
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
	formatter = logging.Formatter(fmt = "%(asctime)s - %(name)s - %(levelname)s: -%(filename)s: %(module)s: - %(exc_info)s - %(process)d: - %(thread)s: - %(threadName)s: - %(message)s")
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
			epoll.register(s.fileno(),selectors.EVENT_READ,accept)
			_logger.info(_("service %s running on %s port %s") % (key, config[key]['host'], config[key]['port'])) 

	if __list_sockets__.keys().__len__() > 0:
		while not _is_shutdown:
			events = epoll.select()
			for key, mask in events:
				callback = key.data
				callback(key,mask)
	else:
		_logger.info(_("Enable services not defined")) 

if __name__ == "__main__":
	main()
