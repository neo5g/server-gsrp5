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

def whandle(server,umsg):
	print('WHANDLE:',dir(server))
	try:
		umsg = server.packer._readfromfp(server, server.rfile)
		if server._BaseServer_shutdown_request:
			ci = obj.getsockname()
			_logger.info(_("Connection closed host:%s port:%s") % (ci[0],ci[1]))
			return False
		else:
			_logger.info('IMessage: %s' % (umsg,))
			if umsg and len(umsg) == 1:
				rmsg = server._dispatcher._execute(umsg[0])
			elif umsg and len(umsg) == 2:
				rmsg = server._dispatcher._execute(umsg[0],umsg[1])
			_logger.info('RMessage: %s' % (rmsg,))
			l = server.packer._writetofp(rmsg, server.wfile)
			return rmsg.__len__() + 10 == l
	except:
		_logger.critical(traceback.format_exc())
		print('TRACEBACK',traceback.format_exc())
		server.packer._writetofp(['E', traceback.format_exc()],wfile)
		return ['E', traceback.format_exc()]

def handle(obj, info, packer):
	ci = obj.getsockname()
	_logger.info(_("Connection on host:%s port:%s") % (ci[0],ci[1]))
	server = Server()
	server._dispatcher = Dispatcher(managers.manager.MetaManager.__list_managers__,os.getcwd())
	server.packer = packer()
	server.rfile = obj.makefile(mode='rb', buffering = -1)
	server.wfile = obj.makefile(mode='wb', buffering = 0)
	selector = _ServerSelector()
	selector.register(obj.fileno(),selectors.EVENT_READ)
	#ep = select.epoll()
	#ep.register(obj.fileno(),select.EPOLLIN|select.EPOLLRDHUP)
	while not server._BaseServer_shutdown_request:
		try:
			ready = selector.select(900)
			if ready:
				umsg = server.packer._readfromfp(server, server.rfile)
				if server._BaseServer_shutdown_request:
					ci = obj.getsockname()
					_logger.info(_("Connection closed host:%s port:%s") % (ci[0],ci[1]))
					break
					_logger.info('IMessage: %s' % (umsg,))
				if umsg and len(umsg) == 1:
					rmsg = server._dispatcher._execute(umsg[0])
				elif umsg and len(umsg) == 2:
					rmsg = server._dispatcher._execute(umsg[0],umsg[1])
				_logger.info('RMessage: %s' % (rmsg,))
				server.packer._writetofp(rmsg, server.wfile)
		except:
			_logger.critical(traceback.format_exc())
			print('TRACEBACK',traceback.format_exc())
			server.packer._writetofp(['E', traceback.format_exc()],server.wfile)
	ep.unregister(obj.fileno())
	ep.close()


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

	epoll = select.epoll()
	
	for key in config['globals'].keys():
		if key in ('tcprpc','tcpv6rpc') and config['globals'][key]:
			s=socket.socket(__list_servicies__[key]['address_family'],__list_servicies__[key]['socket_type'])
			if __list_servicies__[key]['allow_reuse_address']:
				s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
			s.bind((config[key]['host'],config[key]['port']))
			s.listen(5)
			__list_sockets__[s.fileno()] = {'socket':s,'service':key,'handler':__list_servicies__[key]['handler'],'isService':True}
			epoll.register(s.fileno(), select.EPOLLIN)
			_logger.info(_("service %s running on %s port %s") % (key, config[key]['host'], config[key]['port'])) 
	if __list_sockets__.keys().__len__() > 0:
		while not _is_shutdown:
			events = _eintr_retry(epoll.poll)
			for fileno, event in events:
				if event & select.EPOLLRDHUP:
					if fileno in __list_sockets__:
						__list_sockets__[fileno]['socket'].close()
						del __list_sockets__[fileno]
				elif event & select.EPOLLIN:
					if fileno in __list_sockets__ and 'isService' in __list_sockets__[fileno] and __list_sockets__[fileno]['isService']:
						obj,info = __list_sockets__[fileno]['socket'].accept()
						print('ACCEPT:',obj.fileno())
						__list_sockets__[obj.fileno()] = {'socket':obj,'addr_info':info,'handler':__list_servicies__[__list_sockets__[fileno]['service']]['handler'],'service':__list_sockets__[fileno]['service']}
						epoll.register(obj.fileno(), select.EPOLLIN|select.EPOLLRDHUP)
					else:
						print('__LIST_SOCKETS',fileno,__list_sockets__)
						process = Process(target=__list_servicies__[__list_sockets__[fileno]['service']]['handler'],name=__list_sockets__[fileno]['service'],args=(__list_sockets__[fileno]['socket'], __list_sockets__[fileno]['addr_info'], Packer),daemon = config[__list_sockets__[fileno]['service']]['daemon_threads'])
						process.start()
						process.join(0)
						__list_processes__[process.pid] = process
						print('PROCESSES:',process.pid,__list_processes__)
						epoll.unregister(fileno)
						__list_sockets__[fileno]['socket'].close()
						del __list_sockets__[fileno]
	else:
		_logger.info(_("Enable services not defined")) 

if __name__ == "__main__":
	main()
