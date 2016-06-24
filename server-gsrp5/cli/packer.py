# -*- coding: utf-8 -*-

import pickle
import json
import logging

from io import BytesIO

_logger = logging.getLogger("listener."+__name__)

class Serializer(object):

	def dump(self, msg, fp):
		fp.write(msg)

	def load(self, fp):
		return fp.read()

	def dumps(self,msg):
		return msg

	def load(self, msg):
		return msg

class DummySerializer(Serializer): pass

class PickleSerializer(Serializer):

	def dump(self, msg, fp):
		pickle.dump(msg, fp)

	def load(self, fp):
		return pickle.load(fp)

	def dumps(self,msg):
		return pickle.dumps(msg)

	def loads(self, msg):
		return pickle.loads(msg)

class JsonSerializer(Serializer):

	def dump(self, msg, fp):
		json.dump(msg, fp)

	def load(self, fp):
		return json.load(fp)

	def dumps(self,msg):
		return json.dumps(msg)

	def loads(self, msg):
		return json.loads(msg)

class Packer(object):

	_ctx = {}

	_version_protocol = 0

	_content_type = 'D'

	_headers = None

	_msg_version_protocol = '0'

	_msg_content_type = None

	_msg_length = 0

	def __init__(self, msg_content_type):
		self._msg_content_type = msg_content_type
		self._ctx['D'] = DummySerializer()
		self._ctx['P'] = PickleSerializer()
		self._ctx['J'] = JsonSerializer()

	def _readfromfp(self, fp):
		self._headers = fp.read(10).decode('utf-8')
		if self._msg_version_protocol == self._headers[:1]:
			self._msg_length = int(self._headers[2:10], base = 16)
			request = BytesIO()
			request.write(fp.read(self._msg_length))
			if request.tell() == 0:
				_logger.info(_("Error reading socket. Connection closed host:%s port:%s") % (self.connection.getpeername()))
			elif  request.tell() != self._msg_length:
				_logger.info(_("Error reading socket host:%s port:%s") % (self.connection.getpeername()))
				#request.truncate()
				return request
			else:
				request.seek(0,0)
				return self._ctx[self._msg_content_type].load(request)

	def _writetofp(self, msg, fp):
		response = BytesIO()
		self._ctx[self._msg_content_type].dump(msg, response)
		header = ('%1s%1s%08x' % (self._version_protocol, self._msg_content_type, response.tell())).encode('utf-8')
		msg = response.getvalue()
		return fp.write(header + msg)

	def _sendto(self, msg, request, server_address):
		pmsg = self._ctx[self._msg_content_type].dumps(msg)
		return request.sendto('%1s%1s%08x%s' % (self._version_protocol, self._msg_content_type, len(pmsg), pmsg), server_address)

	def _recvfrom(self, request):
		umsg, server_address = request.recvfrom(self.max_packet_size)
		self._headers = umsg[:10]
		msg = umsg[10:]
		if self._msg_version_protocol <= self._headers[:1]:
			self._msg_length = int(self._headers[2:10], base = 16)
			if self._msg_length == len(msg):
				return self._ctx[self._msg_content_type].loads(msg), server_address
		return None
