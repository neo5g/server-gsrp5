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

from socketserver import _ServerSelector, ForkingTCPServer, BaseRequestHandler, StreamRequestHandler, DatagramRequestHandler, ForkingMixIn, ThreadingMixIn, BaseServer, TCPServer, ForkingTCPServer, ThreadingTCPServer, UnixStreamServer, UnixDatagramServer, ForkingUDPServer,ThreadingUDPServer
from pysimplesoap.server import HTTPServer,SOAPHandler
from pysimplesoap.server import SoapDispatcher
import sys
import os
import traceback
import socket
import logging
import ssl
import pickle

import json
import select
from io import StringIO
from tools.translations import trlocal as _

if not "EPOLLRDHUP" in dir(select):
	select.EPOLLRDHUP = 0x2000

_logger = logging.getLogger("listener."+__name__)

class RPCStreamRequestHandler(StreamRequestHandler):
	def handle(self):
		epoll = select.epoll()
		epoll.register(self.connection.fileno(), select.EPOLLIN|select.EPOLLRDHUP)
		while not self.server._BaseServer__shutdown_request:
			try:
				events = _eintr_retry(epoll.poll, self.server.timeout )
				for fileno, event in events:
					if event & select.EPOLLRDHUP:
						ci = self.connection.getsockname()
						_logger.info(_("Connection closed host:%s port:%s") % (ci[0],ci[1]))
						self.server._BaseServer__shutdown_request = True
						break
					elif event & select.EPOLLIN:
						umsg = self.server.serializer._readfromfp(self.server, self.rfile)
						if self.server._BaseServer__shutdown_request:
							break
						_logger.info('IMessage: %s' % (umsg,))
						if umsg and len(umsg) == 1:
							rmsg = self.server._dispatcher._execute(umsg[0])
						elif umsg and len(umsg) == 2:
							rmsg = self.server._dispatcher._execute(umsg[0],umsg[1])
							_logger.info('RMessage: %s' % (rmsg,))
						self.server.serializer._writetofp(rmsg, self.wfile)
			except:
				_logger.critical(traceback.format_exc())
				print('TRACEBACK',traceback.format_exc())
				self.server.serializer._writetofp(['E', traceback.format_exc()],self.wfile)

		epoll.unregister(self.connection.fileno())
		epoll.close()

class UDPService(object):
	def getCountSID(self):
		return('getCountSID')

	def getListSID(self, start, end):
		return('getListSID START=%s, END=%s' % (start,end))

UDPSrv = UDPService()

class RPCDatagramRequestHandler(DatagramRequestHandler):
	_methods = {'getCountSID':UDPSrv.getCountSID,'getListSID':UDPSrv.getListSID}

	def handle(self):
		#umsg = self._read()
		umsg = self.server.serializer._readfromfp(self.server, self.rfile)
		print('IMESSAGE', umsg)
		if self._methods.has_key(umsg[0][0]):
			if umsg.__len__() > 1:
				rmsg =self._methods[umsg[0][0]](**(umsg[1]))
			else:
				rmsg = self._methods[umsg[0][0]]()
			#self._write(rmsg)
			print('RMESSAGE', rmsg)
			self.server.serializer._writetofp(rmsg, self.wfile)

	def _read(self):
		self.rfile.reset()
		return self.server.serializer.load(self.rfile)

	def _write(self, msg):
		return self.server.serializer.dump(msg, self.wfile)

class SSLTCPServer(TCPServer):

	def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True, keyfile = None, certfile = None, cert_reqs = 0, ssl_version = 2, ca_certs = None, do_handshake_on_connect = True, suppress_ragged_eofs = True, ciphers = None ):
		"""Constructor.  May be extended, do not override."""
		super(SSLTCPServer, self).__init__(server_address, RequestHandlerClass)
		self.keyfile = keyfile
		self.certfile = certfile
		self.server_side = True
		self.cert_reqs = cert_reqs
		self.ssl_version = ssl_version
		self.ca_certs = ca_certs
		self.do_handshake_on_connect = do_handshake_on_connect
		self.suppress_ragged_eofs = suppress_ragged_eofs
		self.ciphers = ciphers
		self.socket = socket.socket(self.address_family, self.socket_type)

		if bind_and_activate:
			self.server_bind()
			self.server_activate()

	def server_bind(self):
		"""Called by constructor to bind the socket.

		May be overridden.

		"""
		if self.allow_reuse_address:
			self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socket.bind(self.server_address)
		self.server_address = self.socket.getsockname()

	def server_activate(self):
		"""Called by constructor to activate the server.

		May be overridden.

		"""
		self.socket.listen(self.request_queue_size)

	def server_close(self):
		"""Called to clean-up the server.

		May be overridden.

		"""
		self.socket.close()


	def get_request(self):
		"""Get the request and client address from the socket.
		"""
		client, name = self.socket.accept()
		return ssl.SSLSocket(sock = client, keyfile = self.keyfile, certfile = self.certfile, server_side = self.server_side, cert_reqs = self.cert_reqs, ssl_version = self.ssl_version, ca_certs = self.ca_certs, do_handshake_on_connect = self.do_handshake_on_connect, suppress_ragged_eofs = self.suppress_ragged_eofs, ciphers = self.ciphers), name

if hasattr(socket, 'AF_UNIX'):

	class ForkingUnixStreamServer(ForkingMixIn, UnixStreamServer): pass
	class ForkingUnixDatagramServer(ForkingMixIn, UnixDatagramServer): pass

class ForkingSSLTCPServer(ForkingMixIn, SSLTCPServer): pass
class ThreadingSSLTCPServer(ThreadingMixIn, SSLTCPServer): pass

if hasattr(socket, 'AF_INET6'):

	class ForkingTCPV6Server(ForkingTCPServer):
		address_family = socket.AF_INET6

	class ThreadingTCPV6Server(ThreadingTCPServer):
		address_family = socket.AF_INET6

	class ForkingSSLTCPV6Server(ForkingSSLTCPServer):
		address_family = socket.AF_INET6

	class ThreadingSSLTCPV6Server(ThreadingSSLTCPServer):
		address_family = socket.AF_INET6

	class ForkingUDPV6Server(ForkingUDPServer):
		address_family = socket.AF_INET6

	class ThreadingUDPV6Server(ThreadingUDPServer):
		address_family = socket.AF_INET6


#class ForkingSOAPServer(SOAPServerBase, ForkingTCPServer):

    #def __init__(self, addr = ('localhost', 8000),
        #RequestHandler = SOAPRequestHandler, log = 0, encoding = 'UTF-8',
        #config = Config, namespace = None, ssl_context = None):

        ## Test the encoding, raising an exception if it's not known
        #if encoding != None:
            #''.encode(encoding)

        #if ssl_context != None and not config.SSLserver:
            #raise AttributeError("SSL server not supported by this Python installation")

        #self.namespace          = namespace
        #self.objmap             = {}
        #self.funcmap            = {}
        #self.ssl_context        = ssl_context
        #self.encoding           = encoding
        #self.config             = config
        #self.log                = log

        #self.allow_reuse_address= 1

        #ForkingTCPServer.__init__(self, addr, RequestHandler)

