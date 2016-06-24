# -*- coding: utf-8 -*-

import socket


class addrInfo(object):
	_ibn = {'family':None,'type':None,'proto':None}
	_ibi = {'family':None,'type':None,'proto':None}
	_fl = filter(lambda x: x.isupper and x[:3] == 'AF_',dir(socket))
	_stl = filter(lambda x: x.isupper and x[:5] == 'SOCK_',dir(socket))
	_ipl = filter(lambda x: x.isupper and x[:8] == 'IPPROTO_',dir(socket))
	_aibi = None
	_aibn = []

	def __init__(self,host,port):
		self._aibi = socket.getaddrinfo(host,port)
		for key, value in [['family',self._fl],['type',self._stl],['proto',self._ipl]]:
			self._ibi[key] = self._buildInfoById(value)
			self._ibn[key] = self._buildInfoByName(value)
		for i in self._aibi:
			self._aibn.append((self._ibi['family'][i[0]], self._ibi['type'][i[1]],self._ibi['proto'][i[2]],i[3],i[4]))

	def _buildInfoByName(self,info):
		addrinfo = {}
		for key in info:
			addrinfo[key] = getattr(socket,key)
		return addrinfo

	def _buildInfoById(self,info):
		addrinfo = {}
		for key in info:
			addrinfo[getattr(socket,key)] = key
		return addrinfo

	def _checkInfoByName(self, family, socktype, proto, canonname = ''):
		for info in self._aibn:
			if info[0] == family and info[1] == socktype and info[2] == proto and info[3] == canonname:
				return True
		return False

	def _getInfoByName(self, family, socktype, proto, canonname = ''):
		for info in self._aibn:
			if info[0] == family and info[1] == socktype and info[2] == proto and info[3] == canonname:
				return info
		return None


	def _checkInfoById(self, family, socktype, proto, canonname = ''):
		for info in self._aibi:
			if info[0] == family and info[1] == socktype and info[2] == proto  and info[3] == canonname:
				return True
		return False

	def _getInfoById(self, family, socktype, proto, canonname = ''):
		for info in self._aibi:
			if info[0] == family and info[1] == socktype and info[2] == proto  and info[3] == canonname:
				return info
		return None

	def _getServerAddressByName(self, family, socktype, proto, canonname = ''):
		for info in self._aibn:
			if info[0] == family and info[1] == socktype and info[2] == proto and info[3] == canonname:
				return info[4]
		return None

	def _getServerAddressById(self, family, socktype, proto, canonname = ''):
		for info in self._aibi:
			if info[0] == family and info[1] == socktype and info[2] == proto  and info[3] == canonname:
				return info[4]
		return None


if __name__ == '__main__':
	addrinfo = addrInfo('localhost',8170)
	print(addrinfo._aibn)
	print('checkbyname',addrinfo._checkInfoByName('AF_INET6','SOCK_STREAM','IPPROTO_TCP'))
	print('checkbyid',addrinfo._checkInfoById(10,1,6))
	print('getinfobyname',addrinfo._getInfoByName('AF_INET6','SOCK_STREAM','IPPROTO_TCP'))
	print('getinfobyid',addrinfo._getInfoById(10,1,6))
