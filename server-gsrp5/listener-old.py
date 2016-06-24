# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenGSRP, Open Source Management Solution
#    Copyright (C) 2012- OpenGSRP SA (<http://www.opengsrp.org>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

import os
import sys
import socket
import logging
from logging.handlers import RotatingFileHandler
#import threading
from multiprocessing import Process, freeze_support, active_children
import signal
import socket
import ssl
import time
from os.path import join as opj
from tools.translations import trlocal as _
from tools.packer import Packer
from modules.loading import add_module_paths

add_module_paths(os.getcwd(),{'basic':None,'addons':None})


from socketserver import ForkingTCPServer, ThreadingTCPServer, ForkingUDPServer, ThreadingUDPServer, ThreadingUnixStreamServer, ThreadingUnixDatagramServer
from services.netrpc import ForkingTCPV6Server,ThreadingTCPV6Server, ForkingSSLTCPServer, ForkingSSLTCPV6Server, ThreadingSSLTCPServer,ThreadingSSLTCPV6Server, ForkingUDPV6Server, ThreadingUDPV6Server, ForkingUnixStreamServer, ForkingUnixDatagramServer, RPCStreamRequestHandler, RPCDatagramRequestHandler
#ForkingHTTPServer

from pysimplesoap.server import HTTPServer,SOAPHandler
from pysimplesoap.server import SoapDispatcher

import managers
from dispatcher.dispatcher import Dispatcher
dispathcher = None

__list_thread__ = {}
_logger = logging.getLogger('listener')

def stop(signum,stack):
	_logger.info(_("GSRP Listener stoped"))
	for key in __list_thread__.keys():
		print('TERMINATE:',key,__list_thread__[key], active_children())
		if __list_thread__[key].is_alive():
			__list_thread__[key].terminate()
		#threading.Event().set()
		#__list_thread__[key]._reset_internal_locks()
		#__list_thread__[key]._stop()
		#__list_thread__[key]._delete()
	#threading.shutdown()
	logging.shutdown()
	sys.exit(0)

signal.signal(signal.SIGTERM, stop)
signal.signal(signal.SIGINT, stop)
signal.signal(signal.SIGCHLD, signal.SIG_IGN)

def tcprpcserver(host,port, max_children, timeout, poll_interval, forking, daemon_threads, dispatcher):
	if forking:
		tcprpcserver = ForkingTCPServer(server_address = (host,port), RequestHandlerClass = RPCStreamRequestHandler)
		mode = _('Forking')
	else:
		tcprpcserver = ThreadingTCPServer(server_address = (host,port), RequestHandlerClass = RPCStreamRequestHandler)
		tcprpcserver.daemon_threads = daemon_threads
		mode = _('Threading')
	tcprpcserver.serializer =  Packer()
	tcprpcserver._dispatcher = dispatcher
	tcprpcserver.max_children = max_children
	tcprpcserver.timeout = timeout
	_logger = logging.getLogger("listener.tcprpcserver")
	_logger.info(_("service tcprpc running on %s port %s in mode %s") % (host, port, mode))
	tcprpcserver.serve_forever(poll_interval = poll_interval)

def tcpv6rpcserver(host,port, max_children, timeout, poll_interval, forking, daemon_threads, dispatcher):
	if forking:
		tcpv6rpcserver = ForkingTCPV6Server(server_address = (host,port), RequestHandlerClass = RPCStreamRequestHandler)
		mode = _('Forking')
	else:
		tcpv6rpcserver = ThreadingTCPV6Server(server_address = (host,port), RequestHandlerClass = RPCStreamRequestHandler)
		tcpv6rpcserver.daemon_threads = daemon_threads
		mode = _('Threading')
	tcpv6rpcserver.serializer = Packer()
	tcpv6rpcserver._dispatcher = dispatcher
	tcpv6rpcserver.max_children = max_children
	tcpv6rpcserver.timeout = timeout
	_logger = logging.getLogger("listener.tcpv6rpcserver")
	_logger.info(_("service tcpv6rpc running on %s port %s in mode %s") % (host, port, mode))
	tcpv6rpcserver.serve_forever(poll_interval = poll_interval)


def ssltcprpcserver(host,port, max_children, timeout, poll_interval, forking, daemon_threads, keyfile, certfile, dispatcher):
	if forking:
		ssltcprpcserver = ForkingSSLTCPServer(server_address = (host,port), RequestHandlerClass = RPCStreamRequestHandler, keyfile = keyfile, certfile = certfile, do_handshake_on_connect=False)
		mode = _('Forking')
	else:
		ssltcprpcserver = ThreadingSSLTCPServer(server_address = (host,port), RequestHandlerClass = RPCStreamRequestHandler, keyfile = keyfile, certfile = certfile, do_handshake_on_connect=False)
		ssltcprpcserver.daemon_threads = daemon_threads
		mode = _('Threading')
	ssltcprpcserver.serializer = Packer()
	ssltcprpcserver._dispatcher = dispatcher
	ssltcprpcserver.max_children = max_children
	ssltcprpcserver.timeout = timeout
	_logger = logging.getLogger("listener.ssltcprpcserver")
	_logger.info(_("service ssltcp running on %s port %s in mode %s") % (host, port , mode))
	ssltcprpcserver.serve_forever(poll_interval = poll_interval)

def ssltcpv6rpcserver(host,port, max_children, timeout, poll_interval, forking, daemon_threads, keyfile, certfile, dispatcher):
	if forking:
		ssltcpv6rpcserver = ForkingSSLTCPV6Server(server_address = (host,port), RequestHandlerClass = RPCStreamRequestHandler, keyfile = keyfile, certfile = certfile, do_handshake_on_connect=False)
		mode = _('Forking')
	else:
		ssltcpv6rpcserver = ThreadingSSLTCPV6Server(server_address = (host,port), RequestHandlerClass = RPCStreamRequestHandler, keyfile = keyfile, certfile = certfile, do_handshake_on_connect=False)
		netrpv6csslsrv.daemon_threads = daemon_threads
		mode = _('Threading')
	ssltcpv6rpcserver.serializer = Packer()
	ssltcpv6rpcserver._dispatcher = dispatcher
	ssltcpv6rpcserver.max_children = max_children
	ssltcpv6rpcserver.timeout = timeout
	_logger = logging.getLogger("listener.ssltcpv6rpcserver")
	_logger.info(_("service ssltcpv6 running on %s port %s in mode %s") % (host, port , mode))
	ssltcpv6rpcserver.serve_forever(poll_interval = poll_interval)

def soaprpcserver(host,port, max_children, timeout, poll_interval, forking, daemon_threads, dispatcher):
	def _execute(soapargs, soapkwargs = None):
		if soapkwargs:
			return dispatcher._execute(soapargs.data,soapkwargs._asdict())
		else:
			return dispatcher._execute(soapargs.data)

	if forking:
		soaprpcsrv = ForkingHTTPServer(addr = (host,port), RequestHandler = SOAPRequestHandler)
	else:
		soaprpcsrv = ThreadingHTTPServer(addr = (host,port), RequestHandler = SOAPRequestHandler)
		soaprpcsrv.daemon_threads = daemon_threads
	soaprpcsrv.registerFunction(function = _execute, funcName = 'execute')
	soaprpcsrv.max_children = max_children
	soaprpcsrv.timeout = timeout
	_logger = logging.getLogger("listener.soaprpcserver")
	if forking:
		mode = _('Forking')
	else:
		mode = _('Threading')
	_logger.info(_("service soaprpc running on %s port %s in mode %s") % (host, port, mode))
	soaprpcsrv.serve_forever(poll_interval = poll_interval)

def soaprpcsslserver(host,port, max_children, timeout, poll_interval, forking, daemon_threads, keyfile, certfile, dispatcher):
	def _execute(soapargs, soapkwargs = None):
		if soapkwargs and len(soapkwargs) > 0:
			return dispatcher._execute(soapargs.data,soapkwargs._asdict())
		else:
			return dispatcher._execute(soapargs.data)

	Config.__dict__['key_file'] = keyfile
	Config.__dict__['cert_file'] = certfile
	from OpenSSL import SSL
	ssl_context = SSL.Context(SSL.SSLv23_METHOD)
	ssl_context.use_privatekey_file(keyfile)
	ssl_context.use_certificate_file(certfile)
	if forking:
		soaprpcsslsrv = ForkingHTTPServer(addr = (host,port), RequestHandler = SOAPRequestHandler, ssl_context = ssl_context)
	else:
		soaprpcsslsrv = ThreadingHTTPServer(addr = (host,port), RequestHandler = SOAPRequestHandler, ssl_context = ssl_context)
		soaprpcsslsrv.daemon_threads = daemon_threads
	soaprpcsslsrv.registerFunction(function = _execute, funcName = 'execute')
	soaprpcsslsrv.max_children = max_children
	soaprpcsslsrv.timeout = timeout
	_logger = logging.getLogger("listener.soaprpcsslserver")
	if forking:
		mode = _('Forking')
	else:
		mode = _('Threading')
	_logger.info(_("service sslsoaprpc running on %s port %s in mode %s") % (host, port, mode))
	soaprpcsslsrv.serve_forever(poll_interval = poll_interval)

def udprpcserver(host, port, max_children, timeout, poll_interval, forking, daemon_threads, udpdispatcher):
	if forking:
		udprpcserver = ForkingUDPServer(server_address = (host,port), RequestHandlerClass = RPCDatagramRequestHandler)
		mode = _('Forking')
	else:
		udprpcserver = ThreadingUDPServer(server_address = (host,port), RequestHandlerClass = RPCDatagramRequestHandler)
		udprpcserver.daemon_threads = daemon_threads
		mode = _('Threading')
	udprpcserver.serializer =  Packer()
	udprpcserver._udpdispather = udpdispatcher
	udprpcserver.max_children = max_children
	udprpcserver.timeout = timeout
	_logger = logging.getLogger("listener.udprpcserver")
	_logger.info(_("service utprpc running on %s port %s in mode %s") % (host, port, mode))
	udprpcserver.serve_forever(poll_interval = poll_interval)

def udpv6rpcserver(host, port, max_children, timeout, poll_interval, forking, daemon_threads, udpdispatcher):
	if forking:
		udpv6rpcserver = ForkingUDPV6Server(server_address = (host,port,0,0), RequestHandlerClass = RPCDatagramRequestHandler)
		mode = _('Forking')
	else:
		udpv6rpcserver = ThreadingUDPV6Server(server_address = (host,port), RequestHandlerClass = RPCDatagramRequestHandler)
		udpv6rpcserver.daemon_threads = daemon_threads
		mode = _('Threading')
	udpv6rpcserver.serializer = Packer()
	udpv6rpcserver._udpdispather = udpdispatcher
	udpv6rpcserver.max_children = max_children
	udpv6rpcserver.timeout = timeout
	_logger = logging.getLogger("listener.udpv6rpcserver")
	_logger.info(_("service udpv6rpc running on %s port %s in mode %s") % (host, port, mode))
	udpv6rpcserver.serve_forever(poll_interval = poll_interval)

def unixrpcserver(server_address, max_children, timeout, poll_interval, forking, daemon_threads, dispatcher):
	if os.path.exists(server_address):
		os.unlink(server_address)
	if forking:
		unixrpcserver = ForkingUnixStreamServer(server_address = server_address, RequestHandlerClass = RPCStreamRequestHandler)
		mode = _('Forking')
	else:
		unixrpcserver = ThreadingUnixStreamServer(server_address = server_address, RequestHandlerClass = RPCStreamRequestHandler)
		unixrpcserver.daemon_threads = daemon_threads
		mode = _('Threading')
	unixrpcserver.serializer =  Packer()
	unixrpcserver._dispatcher = dispatcher
	unixrpcserver.max_children = max_children
	unixrpcserver.timeout = timeout
	_logger = logging.getLogger("listener.unixrpcserver")
	_logger.info(_("service unixrpc running on %s  in mode %s") % (server_address, mode))
	unixrpcserver.serve_forever(poll_interval = poll_interval)

def unixudprpcserver(server_address, max_children, timeout, poll_interval, forking, daemon_threads, udpdispatcher):
	if os.path.exists(server_address):
		os.unlink(server_address)
	if forking:
		unixudprpcserver = ForkingingUnixDatagramServer(server_address = server_address, RequestHandlerClass = RPCDatagramRequestHandler)
		mode = _('Forking')
	else:
		unixudprpcserver = ThreadingUnixDatagramServer(server_address = server_address, RequestHandlerClass = RPCDatagramRequestHandler)
		unixudprpcserver.daemon_threads = daemon_threads
		mode = _('Threading')
	unixudprpcserver.serializer =  Packer()
	unixudprpcserver._udpdispatcher = udpdispatcher
	unixudprpcserver.max_children = max_children
	unixudprpcserver.timeout = timeout
	_logger = logging.getLogger("listener.unixudprpcserver")
	_logger.info(_("service unixudprpc running on %s  in mode %s") % (server_address, mode))
	unixudprpcserver.serve_forever(poll_interval = poll_interval)

def main():
	pwd = os.getcwd()
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
	#print 'options',options.__dict__
	config = configManager(CONFIG_FILE)
	global dispathcher
	dispatcher = Dispatcher(managers.manager.MetaManager.__list_managers__,os.getcwd())
	#print('DIR DISPATCHER.DB.PGDB:', dir(dispatcher.db.pgdb))
	formatter = logging.Formatter(fmt = "%(asctime)s - %(name)s - %(levelname)s: -%(filename)s: %(module)s: - %(exc_info)s - %(process)d: - %(thread)s: - %(threadName)s: - %(message)s")
	streamhandler = logging.StreamHandler()
	rotatingfilehandler = RotatingFileHandler('listener.log', maxBytes = 1024*1024, backupCount = 9, encoding = 'UTF-8')
	streamhandler.setFormatter(formatter)
	rotatingfilehandler.setFormatter(formatter)
	_logger.setLevel(logging.INFO)
	_logger.addHandler(streamhandler)
	_logger.addHandler(rotatingfilehandler)

	if config['globals']['tcprpc']:
		__list_thread__['tcprpc'] = Process(target=tcprpcserver, name='tcprpc', args=(config['tcprpc']['host'],config['tcprpc']['port'], config['tcprpc']['max_children'], config['tcprpc']['timeout'], config['tcprpc']['poll_interval'], config['tcprpc']['forking'], config['tcprpc']['daemon_threads'], dispatcher))

	if config['globals']['tcpv6rpc'] and hasattr(socket, "AF_INET6"):
		__list_thread__['tcpv6rpc'] = Process(target=tcpv6rpcserver, name='tcpv6rpc', args=(config['tcpv6rpc']['host'],config['tcpv6rpc']['port'], config['tcpv6rpc']['max_children'], config['tcpv6rpc']['timeout'], config['tcpv6rpc']['poll_interval'], config['tcpv6rpc']['forking'], config['tcpv6rpc']['daemon_threads'], dispatcher))

	if config['globals']['ssltcprpc']:
		__list_thread__['ssltcprpc'] = Process(target=ssltcprpcserver, name='ssltcprpc', args=(config['ssltcprpc']['host'],config['ssltcprpc']['port'], config['ssltcprpc']['max_children'], config['ssltcprpc']['timeout'], config['ssltcprpc']['poll_interval'], config['ssltcprpc']['forking'], config['ssltcprpc']['daemon_threads'], config['ssltcprpc']['keyfile'], config['ssltcprpc']['certfile'], dispatcher))

	if config['globals']['ssltcpv6rpc'] and hasattr(socket, "AF_INET6"):
		__list_thread__['ssltcpv6rpc'] = Process(target=ssltcpv6rpcserver, name='ssltcpv6rpc', args=(config['ssltcpv6rpc']['host'],config['ssltcpv6rpc']['port'], config['ssltcpv6rpc']['max_children'], config['ssltcpv6rpc']['timeout'], config['ssltcpv6rpc']['poll_interval'], config['ssltcpv6rpc']['forking'], config['ssltcpv6rpc']['daemon_threads'], config['ssltcpv6rpc']['keyfile'], config['ssltcpv6rpc']['certfile'], dispatcher))

	if config['globals']['soaprpc']:
		__list_thread__['soaprpc'] = Process(target=soaprpcserver, name='soaprpc', args=(config['soaprpc']['host'],config['soaprpc']['port'], config['soaprpc']['max_children'], config['soaprpc']['timeout'], config['soaprpc']['poll_interval'], config['soaprpc']['forking'], config['soaprpc']['daemon_threads'], dispatcher))

	if config['globals']['sslsoaprpc']:
		__list_thread__['sslsoaprpc'] = Process(target=soaprpcsslserver, name='sslsoaprpc', args=(config['sslsoaprpc']['host'],config['sslsoaprpc']['port'], config['sslsoaprpc']['max_children'], config['sslsoaprpc']['timeout'], config['sslsoaprpc']['poll_interval'], config['sslsoaprpc']['forking'], config['sslsoaprpc']['daemon_threads'], config['sslsoaprpc']['keyfile'], config['sslsoaprpc']['certfile'], dispatcher))

	if config['globals']['unixrpc'] and hasattr(socket, "AF_UNIX"):
		__list_thread__['unixrpc'] = Process(target=unixrpcserver, name='unixrpc', args=(config['unixrpc']['server_address'], config['unixrpc']['max_children'], config['unixrpc']['timeout'], config['unixrpc']['poll_interval'], config['unixrpc']['forking'], config['unixrpc']['daemon_threads'], dispatcher))

	if config['globals']['unixudprpc'] and hasattr(socket, "AF_UNIX"):
		__list_thread__['unixudprpc'] = Process(target=unixudprpcserver, name='unixudprpc', args=(config['unixudprpc']['server_address'], config['unixudprpc']['max_children'], config['unixudprpc']['timeout'], config['unixudprpc']['poll_interval'], config['unixudprpc']['forking'], config['unixudprpc']['daemon_threads'], dispatcher))


	if config['globals']['udprpc']:
		__list_thread__['udprpc'] = Process(target=udprpcserver, name='udprpc', args=(config['udprpc']['host'],config['udprpc']['port'], config['udprpc']['max_children'], config['udprpc']['timeout'], config['udprpc']['poll_interval'], config['udprpc']['forking'], config['udprpc']['daemon_threads'], dispatcher))

	if config['globals']['udpv6rpc'] and hasattr(socket, "AF_INET6"):
		__list_thread__['udpv6rpc'] = Process(target=udpv6rpcserver, name='udpv6rpc', args=(config['udpv6rpc']['host'],config['udpv6rpc']['port'], config['udpv6rpc']['max_children'], config['udpv6rpc']['timeout'], config['udpv6rpc']['poll_interval'], config['udpv6rpc']['forking'], config['udpv6rpc']['daemon_threads'], dispatcher))

	freeze_support()
	for key in __list_thread__.keys():
		__list_thread__[key].start()
		print('Started:', key)
		if __list_thread__[key].is_alive():
			__list_thread__[key].join(1)

if __name__ == '__main__':
	main()

