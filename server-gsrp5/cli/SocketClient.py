import socket
import ssl
try:
	import cPickle as pickle
except:
	import pickle
import json
import logging
#from tools.addrinfo import addrInfo
from cli.addrinfo import addrInfo
import sys
from cli.packer import Packer

try:
	from cStringIO import StringIO
except ImportError:
	from io import StringIO

_logger = logging.getLogger('webserver.' + __name__)

__all__ = ["NetRPCTCPClient","NetRPCSSLTCPClient","JsonRPCTCPClient","JsonRPCSSLTCPClient","NetDatagramTCPClient","JsonDatagramTCPClient"]

if hasattr(socket, "AF_UNIX"):
	__all__.extend(["NetDatagramTCPClient","JsonDatagramTCPClient",
                    "NetDatagramUnixClient",
                    "JsonDatagramUnixClient"])

if hasattr(socket, "AF_INET6"):
	__all__.extend(["NetRPCTCPV6Client","NetRPCSSLTCPV6Client","JsonRPCTCPV6Client","JsonRPCSSLTCPV6Client","NetDatagramTCPV6Client","JsonDatagramTCPV6Client"])

class BaseRequestHandler(object):

	rbufsize = -1

	wbufsize = 0

	max_msg_size = 0xffffffff

	max_packet_size = 1024

	len_msg_size = 8

	_packer = None

	_unpacker = None

	def __init__(self, request, client_address, server_address):
		self.request = request
		if self.request.family == socket.AF_UNIX and self.request.type == socket.SOCK_STREAM:
			self.max_packet_size = 32768
		elif self.request.type == socket.SOCK_DGRAM:
			self.max_packet_size = 8192
		self.server_address = server_address
		self.client_address = client_address
		self.rfile = self.request.makefile('rb', self.rbufsize)
		self.wfile = self.request.makefile('wb', self.wbufsize)


	def handle(self,msg):
		pass

	def _read(self):
		pass

	def _write(self):
		pass

class StreamRequestHandler(BaseRequestHandler):

	def handle(self,msg):
		self.serializer._writetofp(msg, self.wfile)
		return self.serializer._readfromfp(self.rfile)

class BaseClient(object):

	rbufsize = -1

	wbufsize = 0

	len_msg_size = 8

	max_packet_size = 1024

	def __init__(self, server_address, requestHandlerClass, serializerClass,timeout = 900, activate=True):
		if self.address_family == socket.AF_INET or self.address_family == socket.AF_INET6:
			self.addrinfo = addrInfo(host = server_address[0],port = server_address[1])

		if not hasattr(self,'socket_proto'):
			self.socket_proto = 0

		if not hasattr(self,'socket_canonname'):
			self.socket_canonname = ''

		if (self.address_family == socket.AF_INET or self.address_family == socket.AF_INET6) and self.addrinfo._checkInfoById(self.address_family, self.socket_type, self.socket_proto, self.socket_canonname):
			self.server_address = self.addrinfo._getServerAddressById(self.address_family, self.socket_type, self.socket_proto, self.socket_canonname)
		else:
			self.server_address = server_address
		self.socket = socket.socket(self.address_family, self.socket_type, self.socket_proto)
		self.requestHandlerClass = requestHandlerClass
		self.serializerClass = serializerClass
		self.timeout = timeout
		self.activate = activate
		if activate:
			self.client_activate()

	def client_activate(self):
		self.socket.connect(self.server_address)
		self.client_address = self.socket.getsockname()
		self.socket.settimeout(self.timeout)
		self.requestHandler = self.requestHandlerClass(self.socket, self.client_address, self.server_address)
		self.requestHandler.serializer = self.serializerClass(self._msg_content_type)

	def client_close(self):
		self.requestHandler.rfile.close()
		self.requestHandler.wfile.close()
		self.socket.close()

	def handle(self, msg):
		if hasattr(self.socket,'_closed') and not self.socket._closed:
			return self.requestHandler.handle(msg)
		else:
			try:
				self.socket = socket.socket(self.address_family, self.socket_type)
				self.client_activate()
				return self.requestHandler.handle(msg)
			except (socket.error,socket.timeout):
				_logger.error(_('Error connect to server host:%s port:%s') % (self.server_address[0],self.server_address[1]))


class SSLBaseClient(object):

	rbufsize = -1

	wbufsize = 0

	len_msg_size = 8

	max_packet_size = 1024

	def __init__(self, server_address, requestHandlerClass, serializerClass, keyfile = None, certfile = None, server_side = False, cert_reqs = 0, ssl_version = 2, ca_certs = None, do_handshake_on_connect = True, suppress_ragged_eofs = True, ciphers = None, timeout = 900, activate = True ):
		if self.address_family == socket.AF_INET or self.address_family == socket.AF_INET6:
			self.addrinfo = addrInfo(host = server_address[0],port = server_address[1])

		if not hasattr(self,'socket_proto'):
			self.socket_proto = 0

		if not hasattr(self,'socket_canonname'):
			self.socket_canonname = ''

		if (self.address_family == socket.AF_INET or self.address_family == socket.AF_INET6) and self.addrinfo._checkInfoById(self.address_family, self.socket_type, self.socket_proto, self.socket_canonname):
			self.server_address = self.addrinfo._getServerAddressById(self.address_family, self.socket_type, self.socket_proto, self.socket_canonname)
		else:
			self.server_address = server_address
		self.client = socket.socket(self.address_family, self.socket_type, self.socket_proto)
		self.requestHandlerClass = requestHandlerClass
		self.serializerClass = serializerClass
		self.keyfile = keyfile
		self.certfile = certfile
		self.server_side = server_side = False
		self.cert_reqs = cert_reqs
		self.ssl_version = ssl_version
		self.ca_certs = ca_certs
		self.do_handshake_on_connect = do_handshake_on_connect
		self.suppress_ragged_eofs = suppress_ragged_eofs
		self.ciphers = ciphers
		self.socket = ssl.SSLSocket(sock = self.client, keyfile = self.keyfile, certfile = self.certfile, server_side = self.server_side, cert_reqs = self.cert_reqs, ssl_version = self.ssl_version, ca_certs = self.ca_certs, do_handshake_on_connect = self.do_handshake_on_connect, suppress_ragged_eofs = self.suppress_ragged_eofs, ciphers = self.ciphers)
		self.timeout = timeout
		if activate:
			self.client_activate()

	def client_activate(self):
		self.socket.connect(self.server_address)
		self.client_address = self.socket.getsockname()
		self.socket.settimeout(self.timeout)
		self.requestHandler = self.requestHandlerClass(self.socket, self.server_address, self.socket.getpeername())
		self.requestHandler.serializer = self.serializerClass(self._msg_content_type)

	def client_close(self):
		self.requestHandler.rfile.close()
		self.requestHandler.wfile.close()
		self.socket.close()

	def handle(self, msg):
		if hasattr(self.socket,'_closed') and  not self.socket._closed:
			return self.requestHandler.handle(msg)
		else:
			try:
				self.client = socket.socket(self.address_family, self.socket_type)
				self.client_activate()
				self.socket = ssl.SSLSocket(sock = self.client, keyfile = self.keyfile, certfile = self.certfile, server_side = self.server_side, cert_reqs = self.cert_reqs, ssl_version = self.ssl_version, ca_certs = self.ca_certs, do_handshake_on_connect = self.do_handshake_on_connect, suppress_ragged_eofs = self.suppress_ragged_eofs, ciphers = self.ciphers)
				return self.requestHandler.handle(msg)
			except (socket.error,socket.timeout):
				_logger.error(_('Error connect to server host:%s port:%s') % (self.server_address[0],self.server_address[1]))



class TCPClient(BaseClient):

	address_family = socket.AF_INET

	socket_type = socket.SOCK_STREAM

	socket_proto = socket.IPPROTO_TCP

	allow_reuse_address = False

class SSLTCPClient(SSLBaseClient):

	address_family = socket.AF_INET

	socket_type = socket.SOCK_STREAM

	socket_proto = socket.IPPROTO_TCP

	allow_reuse_address = False

class NetRPCTCPClient(TCPClient):
	_msg_content_type = 'P'
	def __init__(self, server_address, requestHandlerClass = StreamRequestHandler, serializerClass = Packer,activate=True):
		super(NetRPCTCPClient, self).__init__(server_address = server_address, requestHandlerClass = requestHandlerClass, serializerClass = serializerClass, activate=activate)

class NetRPCSSLTCPClient(SSLTCPClient):
	_msg_content_type = 'P'
	def __init__(self,  server_address, requestHandlerClass = StreamRequestHandler, serializerClass = Packer, keyfile = None, certfile = None, server_side = False, cert_reqs = 0, ssl_version = 2, ca_certs = None, do_handshake_on_connect = True, suppress_ragged_eofs = True, ciphers = None, activate = True):
		super(NetRPCSSLTCPClient, self).__init__(server_address = server_address, requestHandlerClass = requestHandlerClass, serializerClass = serializerClass, keyfile = keyfile, certfile = certfile, activate=activate)

class JsonRPCTCPClient(TCPClient):
	_msg_content_type = 'J'
	def __init__(self, server_address, requestHandlerClass = StreamRequestHandler, serializerClass = Packer,activate=True):
		super(JsonRPCTCPClient, self).__init__(server_address = server_address, requestHandlerClass = requestHandlerClass, serializerClass = serializerClass, activate=activate)

class JsonRPCSSLTCPClient(SSLTCPClient):
	_msg_content_type = 'J'
	def __init__(self,  server_address, requestHandlerClass = StreamRequestHandler, serializerClass = Packer, keyfile = None, certfile = None, server_side = False, cert_reqs = 0, ssl_version = 2, ca_certs = None, do_handshake_on_connect = True, suppress_ragged_eofs = True, ciphers = None, activate = True):
		super(JsonRPCSSLTCPClient, self).__init__(server_address = server_address, requestHandlerClass = requestHandlerClass, serializerClass = serializerClass, keyfile = keyfile, certfile = certfile, activate=activate)

class DatagramRequestHandler(BaseRequestHandler):

	def handle(self,msg):
		self.serializer._sendto(msg, self.request, self.server_address)
		msg, server_address = self.serializer._recvfrom(self.request)
		return msg

class BaseUDPClient(object):

	rbufsize = -1

	wbufsize = 0

	len_msg_size = 8

	max_packet_size = 8192

	def __init__(self, server_address, requestHandlerClass, serializerClass, activate = True):
		self.server_address = server_address
		self.socket = socket.socket(self.address_family,self.socket_type, self.socket_proto)
		self.requestHandlerClass = requestHandlerClass
		self.serializerClass = serializerClass
		if activate:
			self.client_activate()

	def handle(self, msg):
		return self.requestHandler.handle(msg)

	def client_activate(self):
		self.requestHandler = self.requestHandlerClass(self.socket, self.server_address, self.server_address)
		self.requestHandler.serializer = self.serializerClass(self._msg_content_type)
		self.requestHandler.serializer.max_packet_size = self.max_packet_size

	def client_close(self):
		pass

class UDPClient(BaseUDPClient):

	address_family = socket.AF_INET

	socket_type = socket.SOCK_DGRAM

	socket_proto = socket.IPPROTO_UDP

	allow_reuse_address = False

	max_packet_size = 8192

class NetRPCUDPClient(UDPClient):
	_msg_content_type = 'P'
	def __init__(self, server_address, requestHandlerClass =  DatagramRequestHandler, serializerClass = Packer, activate = True):
		super(NetRPCUDPClient, self).__init__(server_address = server_address, requestHandlerClass = requestHandlerClass, serializerClass = serializerClass, activate = activate)

class JsonRPCUDPClient(UDPClient):
	_msg_content_type = 'J'
	def __init__(self, server_address, requestHandlerClass =  DatagramRequestHandler, serializerClass = Packer, activate = True):
		super(JsonRPCUDPClient, self).__init__(server_address = server_address, requestHandlerClass = requestHandlerClass, serializerClass = serializerClass, activate = activate)

if hasattr(socket, 'AF_UNIX'):
	class NetRPCUnixClient(TCPClient):

		address_family = socket.AF_UNIX

		socket_proto = 0

		_msg_content_type = 'P'

		def __init__(self, server_address, requestHandlerClass = StreamRequestHandler, serializerClass = Packer,  activate=True):
			super(NetRPCUnixClient ,self).__init__(server_address = server_address, requestHandlerClass = requestHandlerClass,serializerClass = serializerClass, activate=activate)

	class JsonRPCUnixClient(TCPClient):

		address_family = socket.AF_UNIX

		socket_proto = 0

		_msg_content_type = 'J'

		def __init__(self, server_address, requestHandlerClass = StreamRequestHandler, serializerClass = Packer,  activate=True):
			super(JsonRPCUnixClient ,self).__init__(server_address = server_address, requestHandlerClass = requestHandlerClass,serializerClass = serializerClass, activate=activate)


	class NetRPCUnixUDPClient(UDPClient):

		address_family = socket.AF_UNIX

		_msg_content_type = 'P'

		def __init__(self, server_address, requestHandlerClass =  DatagramRequestHandler, serializerClass = Packer, activate=True):
			super(NetRPCUnixUDPClient ,self).__init__(server_address = server_address, requestHandlerClass = requestHandlerClass, serializerClass = serializerClass, activate = activate)

	class JsonRPCUnixUDPClient(UDPClient):

		address_family = socket.AF_UNIX

		_msg_content_type = 'J'

		def __init__(self, server_address, requestHandlerClass =  DatagramRequestHandler, serializerClass = Packer, activate=True):
			super(JsonRPCUnixUDPClient ,self).__init__(server_address = server_address, requestHandlerClass = requestHandlerClass, serializerClass = serializerClass, activate = activate)

if hasattr(socket, 'AF_INET6'):
	class NetRPCTCPV6Client(NetRPCTCPClient):

		address_family = socket.AF_INET6

		_msg_content_type = 'P'

	class NetRPCSSLTCPV6Client(NetRPCSSLTCPClient):

		address_family = socket.AF_INET6

		_msg_content_type = 'P'

	class JsonRPCTCPV6Client(JsonRPCTCPClient):

		address_family = socket.AF_INET6

		_msg_content_type = 'J'

	class JsonRPCSSLTCPV6Client(JsonRPCSSLTCPClient):

		address_family = socket.AF_INET6

		_msg_content_type = 'J'

	class NetRPCUDPV6Client(NetRPCUDPClient):

		address_family = socket.AF_INET6

		_msg_content_type = 'P'

	class JsonRPCUDPV6Client(JsonRPCUDPClient):

		address_family = socket.AF_INET6

		_msg_content_type = 'J'

if __name__ == '__main__':
	clnt = NetRPCTCPClient(('localhost',8170))
	print('NetRPCTCPClient login', clnt.handle([['app.db.db.login'],{'host':'localhost','port':5432,'database':'postgres','user':'postgres','password':'admin'}]))
	print('NetRPCTCPClient Logout', clnt.handle([['app.db.db.logout']]))
	clnt.client_close()

	clnt = NetRPCTCPV6Client(('localhost',8170))
	print('NetRPCTCPV6Client login', clnt.handle([['app.db.db.login'],{'host':'localhost','port':5432,'database':'postgres','user':'postgres','password':'admin'}]))
	print('NetRPCTCPV6Client Logout', clnt.handle([['app.db.db.logout']]))
	clnt.client_close()

	clnt = NetRPCSSLTCPClient(('localhost',8171), keyfile = '../localhost.localdomain.key', certfile = '../localhost.localdomain.crt')
	print('NetRPCSSLTCPClient login', clnt.handle([['app.db.db.login'],{'host':'localhost','port':5432,'database':'postgres','user':'postgres','password':'admin'}]))
	print('NetRPCSSLTCPClient Logout', clnt.handle([['app.db.db.logout']]))
	clnt.client_close()

	clnt = NetRPCSSLTCPV6Client(('localhost',8171), keyfile = '../localhost.localdomain.key', certfile = '../localhost.localdomain.crt')
	print('NetRPCSSLTCPV6Client login', clnt.handle([['app.db.db.login'],{'host':'localhost','port':5432,'database':'postgres','user':'postgres','password':'admin'}]))
	print('NetRPCSSLTCPV6Client Logout', clnt.handle([['app.db.db.logout']]))
	clnt.client_close()

	clnt = JsonRPCTCPClient(('localhost',8170))
	print('JsonRPCTCPClient login', clnt.handle([['app.db.db.login'],{'host':'localhost','port':5432,'database':'postgres','user':'postgres','password':'admin'}]))
	print('JsonRPCTCPClient Logout', clnt.handle([['app.db.db.logout']]))
	clnt.client_close()

	clnt = JsonRPCTCPV6Client(('localhost',8170))
	print('JsonRPCTCPV6Client login', clnt.handle([['app.db.db.login'],{'host':'localhost','port':5432,'database':'postgres','user':'postgres','password':'admin'}]))
	print('JsonRPCTCPV6Client Logout', clnt.handle([['app.db.db.logout']]))
	clnt.client_close()

	clnt = JsonRPCSSLTCPClient(('localhost',8171), keyfile = '../localhost.localdomain.key', certfile = '../localhost.localdomain.crt')
	print('JsonRPCSSLTCPClient login', clnt.handle([['app.db.db.login'],{'host':'localhost','port':5432,'database':'postgres','user':'postgres','password':'admin'}]))
	print('NetRPCSSLTCPClient Logout', clnt.handle([['app.db.db.logout']]))
	clnt.client_close()

	clnt = JsonRPCSSLTCPV6Client(('localhost',8171), keyfile = '../localhost.localdomain.key', certfile = '../localhost.localdomain.crt')
	print('JsonRPCSSLTCPV6Client login', clnt.handle([['app.db.db.login'],{'host':'localhost','port':5432,'database':'postgres','user':'postgres','password':'admin'}]))
	print('NetRPCSSLTCPV6Client Logout', clnt.handle([['app.db.db.logout']]))
	clnt.client_close()

	clnt = NetRPCUDPClient(('localhost',8170))
	print('NetRPCDatagramTCPClient getCountSID', clnt.handle([['getCountSID']]))
	print('NetRPCDatagramTCPClient getListSID', clnt.handle([['getListSID'],{'start':5,'end':7}]))
	clnt.client_close()

	clnt = NetRPCUDPV6Client(('localhost',8170))
	print('NetRPCDatagramTCPV6Client getCountSID', clnt.handle([['getCountSID']]))
	print('NetRPCDatagramTCPV6Client getListSID', clnt.handle([['getListSID'],{'start':5,'end':7}]))
	clnt.client_close()

	clnt = JsonRPCUDPClient(('localhost',8170))
	print('JsonRPCDatagramTCPClient getCountSID', clnt.handle([['getCountSID']]))
	clnt = JsonRPCUDPClient(('localhost',8170))
	print('JsonRPCDatagramTCPClient getListSID', clnt.handle([['getListSID'],{'start':5,'end':7}]))
	clnt.client_close()

	clnt = JsonRPCUDPV6Client(('localhost',8170))
	print('JsonRPCDatagramTCPV6Client getCountSID', clnt.handle([['getCountSID']]))
	clnt = JsonRPCUDPV6Client(('localhost',8170))
	print('JsonRPCDatagramTCPV6Client getListSID', clnt.handle([['getListSID'],{'start':5,'end':7}]))
	clnt.client_close()

	clnt = NetRPCUnixClient('/tmp/gsrp-unixrpc')
	print('NetRPCUnixClient login', clnt.handle([['app.db.db.login'],{'host':'localhost','port':5432,'database':'postgres','user':'postgres','password':'admin'}]))
	print('NetRPCUnixClient logout', clnt.handle([['app.db.db.logout']]))
	clnt.client_close()

	clnt = JsonRPCUnixClient('/tmp/gsrp-unixrpc')
	print('JsonRPCUnixClient login', clnt.handle([['app.db.db.login'],{'host':'localhost','port':5432,'database':'postgres','user':'postgres','password':'admin'}]))
	print('JsonRPCUnixClient logout', clnt.handle([['app.db.db.logout']]))
	clnt.client_close()



	clnt = NetRPCUnixUDPClient('/tmp/gsrp-unixudprpc')
	print('NetRPCUnixClient login', clnt.handle([['app.db.db.login'],{'host':'localhost','port':5432,'database':'postgres','user':'postgres','password':'admin'}]))
	print('NetRPCUnixClient logout', clnt.handle([['app.db.db.logout']]))
	clnt.client_close()

	clnt = JsonRPCUnixUDPClient('/tmp/gsrp-unixudprpc')
	print('JsonRPCUnixClient login', clnt.handle([['app.db.db.login'],{'host':'localhost','port':5432,'database':'postgres','user':'postgres','password':'admin'}]))
	print('JsonRPCUnixClient logout', clnt.handle([['app.db.db.logout']]))
	clnt.client_close()
