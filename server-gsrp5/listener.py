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

oauth2_in = Queue()
oauth2_out = Queue()


# Start of new handlers

def oauth2Handle(oauth2_in,oauth2_out):
	_logger.info("Running oauth2 service")
	entry = {}
	while True:
		msg = oauth2_in.get()
		if msg is None:
			break
		method = msg[0]
		if method in entry:
			if len(msg) == 1:
				oauth2_out.puth(entry[method]())
			elif len(msg) == 1:
				oauth2_out.puth(entry[method](**(msg[1])))
	_logger.info("Stoped oauth2 service")

def tHandle(pinq,nf,config):
	epoll = _ServerSelector()
	epoll.register(__list_sockets__[nf]['socket'],selectors.EVENT_READ)
	_is_shutdown = False
	while not _is_shutdown:		
		events = epoll.select(config[__list_sockets__[nf]['service']]['timeout'])
		for key,mask in events:
			server = __list_sockets__[key.fd]['server']
			msg = server.packer._readfromfp(server, server.rfile)
			if __list_sockets__[key.fd]['socket']._closed or len(msg) == 0:
				epoll.unregister(__list_sockets__[key.fd]['socket'])
				epoll.close()
				server.rfile.close()
				server.wfile.flush()
				server.wfile.close()
				obj = __list_sockets__[key.fd]
				obj['socket'].close()
				_logger.info('Connection closed host %s port %s' % (obj['info'][0],obj['info'][1]))
				if key.fd in __list_sockets__:
					del __list_sockets__[key.fd]
				_is_shutdown = True
				break
			else:
				imsg = [nf]
				imsg.extend(msg)	
				pinq.put(imsg)
		
def inqHandle(inq,pinq):
	while True:		
		km = inq.get()
		if km is None:
			break
		key,mask = km
		if not key.fd in __list_sockets__:
			continue
		server = __list_sockets__[key.fd]['server']
		msg = server.packer._readfromfp(server, server.rfile)
		if len(msg) == 0:
			epoll.unregister(key.fileobj)
			server.rfile.close()
			server.wfile.flush()
			server.wfile.close()
			obj = __list_sockets__[key.fd]
			obj['socket'].close()
			_logger.info('Connection closed host %s port %s' % (obj['info'][0],obj['info'][1]))
			if key.fd in __list_sockets__:
				del __list_sockets__[key.fd]
			continue

		imsg = [key.fd]
		imsg.extend(msg)	
		pinq.put(imsg)

def outqHandle(poutq):

	while True:
		msg = poutq.get()
		if msg is None:
			break
		chan = msg[0]
		rmsg = msg[1:]
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
	epoll.unregister(key.fileobj)
	inq.put([key,mask])

		
def tcpAccept(key,mask,config):
	conn, addr = __list_sockets__[key.fd]['socket'].accept()
	conn.setblocking(True)
	service = __list_sockets__[key.fd]['service']
	conn.settimeout(config[service]['timeout'])
	conn.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,True)
	server = Server()
	server.packer = Packer()
	server.rfile = conn.makefile(mode='rb', buffering = -1)
	server.wfile = conn.makefile(mode='wb', buffering = 0)
	ci = conn.getsockname()
	__list_sockets__[conn.fileno()] = {'socket':conn,'server':server,'address':addr,'info':ci,'service':__list_sockets__[key.fd]['service']}
	_logger.info(_("Connect on host %s port %s") % (ci[0],ci[1]))
	nm = 'tcphandle-%s' % conn.fileno()
	__list_processes__[nm] = threading.Thread(group=None,target=tHandle,name=nm,args=(pinq,conn.fileno(),config),daemon=False)
	__list_processes__[nm].start()

def SSLtcpAccept(key,mask,config):
	conn, addr = __list_sockets__[key.fd]['socket'].accept()
	attr = config[__list_sockets__[key.fd]['service']]
	sslconn = ssl.SSLSocket(sock = conn, keyfile = attr['keyfile'], certfile = attr['certfile'], server_side = True, cert_reqs = 0, ssl_version = 2, ca_certs = None, do_handshake_on_connect = True, suppress_ragged_eofs = True, ciphers = None)
	sslconn.setblocking(True)
	sslconn.settimeout(attr['timeout'])
	sslconn.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,True)
	server = Server()
	server.packer = Packer()
	server.rfile = sslconn.makefile(mode='rb', buffering = -1)
	server.wfile = sslconn.makefile(mode='wb', buffering = 0)
	ci = sslconn.getsockname()
	__list_sockets__[sslconn.fileno()] = {'socket':sslconn,'server':server,'address':addr,'info':ci,'service':__list_sockets__[key.fd]['service']}
	_logger.info(_("Connect on host %s port %s") % (ci[0],ci[1]))
	nm = 'ssltcphandle-%s' % sslconn.fileno()
	__list_processes__[nm] = threading.Thread(group=None,target=tHandle,name=nm,args=(pinq,sslconn.fileno(),config),daemon=False)
	__list_processes__[nm].start()

def udpAccept(key,mask,config):
	pass

def main():
	__list_servicies__ = {}
	__list_servicies__['tcprpc'] = {'address_family':socket.AF_INET,'socket_type':socket.SOCK_STREAM,'allow_reuse_address':False,'handler':tcpAccept}
	__list_servicies__['tcpv6rpc'] = {'address_family':socket.AF_INET6,'socket_type':socket.SOCK_STREAM,'allow_reuse_address':False,'handler':tcpAccept}
	__list_servicies__['ssltcprpc'] = {'address_family':socket.AF_INET,'socket_type':socket.SOCK_STREAM,'allow_reuse_address':False,'handler':SSLtcpAccept}
	__list_servicies__['ssltcpv6rpc'] = {'address_family':socket.AF_INET6,'socket_type':socket.SOCK_STREAM,'allow_reuse_address':False,'handler':SSLtcpAccept}
	__list_servicies__['unixrpc'] = {'address_family':socket.AF_UNIX,'socket_type':socket.SOCK_STREAM,'allow_reuse_address':False,'handler':tcpAccept}
	__list_servicies__['udprpc'] = {'address_family':socket.AF_INET,'socket_type':socket.SOCK_DGRAM,'allow_reuse_address':False,'handler':udpAccept}
	__list_servicies__['unixudprpc'] = {'address_family':socket.AF_INET,'socket_type':socket.SOCK_DGRAM,'allow_reuse_address':False,'handler':udpAccept}
	__list_servicies__['udpv6rpc'] = {'address_family':socket.AF_INET6,'socket_type':socket.SOCK_DGRAM,'allow_reuse_address':False,'handler':udpAccept}
	__list_servicies__['soaprpc'] = None
	__list_servicies__['sslsoaprpc'] = None
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
	threads = []
	for key in config['globals'].keys():
		if  config['globals'][key] and key in __list_servicies__ and __list_servicies__[key]:
			s=socket.socket(__list_servicies__[key]['address_family'],__list_servicies__[key]['socket_type'])
			if __list_servicies__[key]['allow_reuse_address']:
				s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
			if key in ('tcprpc','tcpv6rpc','ssltcprpc','ssltcpv6rpc','unixrpc'):
				if key == 'unixrpc':
					if os.path.exists(config[key]['server_address']):
						os.unlink(config[key]['server_address'])
					s.bind(config[key]['server_address'])
				else:
					s.bind((config[key]['host'],config[key]['port']))
				s.listen(5)
			elif key in ('udprpc','unixudprpc','udpv6rpc'):
				if key in ('unixrpc','unixudprcp'):
					if os.path.exists(config[key]['server_address']):
						os.unlink(config[key]['server_address'])
					s.bind(config[key]['server_address'])
				else:
					s.bind((config[key]['host'],config[key]['port']))
			__list_sockets__[s.fileno()] = {'socket':s,'service':key}
			s.setblocking(True)
			reg =  epoll.register(s,selectors.EVENT_READ,__list_servicies__[key]['handler'])
			__list_sockets__[reg.fd]['reg'] = reg
			if key in ('unixrpc','unixudprcp'):
				_logger.info(_("service %s listening on %s") % (key, config[key]['server_address'],)) 
			else:
				_logger.info(_("service %s listening on %s port %s") % (key, config[key]['host'], config[key]['port'])) 
	print(list(__list_sockets__.keys()))

	if __list_sockets__.keys().__len__() > 0:
		for i in range(cpu_count()*2):
			nm = 'outqhandle-%s' % i
			__list_processes__[nm] = threading.Thread(group=None,target=outqHandle,name=nm,args=(outq,),daemon=False)
			nm = 'worker-%s' % i
			__list_processes__[nm] = Process(group=None,target=pinqHandle,name=nm,args=(pinq,outq),kwargs={},daemon=None)
		nm = 'oauth2'
		__list_processes__[nm] = Process(group=None,target=oauth2Handle,name=nm,args=(oauth2_in,oauth2_out),kwargs={},daemon=None)
		for thread in __list_processes__.keys():
			__list_processes__[thread].start()

		while not _is_shutdown:
			events = epoll.select()
			for key, mask in events:
				if key.fd in __list_sockets__:
					callback = key.data
					callback(key,mask,config)
				else:
					epoll.unregister(key.fileobj)
	else:
		_logger.info(_("Enable services not defined")) 


if __name__ == "__main__":
	main()
