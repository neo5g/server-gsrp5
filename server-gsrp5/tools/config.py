# -*- coding: utf-8 -*-

import os
from os.path import join as opj
try:
	from ConfigParser  import ConfigParser
except:
	from configparser  import ConfigParser
import optparse
import copy
import logging

_logger= logging.getLogger(__name__)
handler = logging.StreamHandler()
_logger.setLevel(logging.INFO)
_logger.addHandler(handler)

SERVICE_GLOBAL_DEFAULT = (('tcprpc',True),('tcpv6rpc',True),('ssltcprpc',False),('ssltcpv6rpc',False),('soaprpc',True),('sslsoaprpc',False),('udprpc',False),('udpv6rpc',False), ('unixrpc',False),('unixudprpc',False), ('logfile','/var/log/gsrp/gsrp-connector.log'),('pidfile','/var/log/gsrp/gsrp-connector.pid'))

SERVICE_TCPRPC_DEFAULT = (('host','localhost.localdomain'),('port',8170),('max_children',100), ('timeout',900),('poll_interval',10),('forking',True),('daemon_threads',False))
SERVICE_SSLTCPRPC_DEFAULT = (('host','localhost.localdomain'),('port',8171),('max_children',100), ('timeout',900),('poll_interval',10),('forking',True),('daemon_threads',False), ('keyfile', 'localhost.localdomain.key'),('certfile','localhost.localdomain.crt'))

SERVICE_SOAPRPC_DEFAULT = (('host','localhost.localdomain'),('port',8172),('max_children',100), ('timeout',900),('poll_interval',10),('forking',True),('daemon_threads',False))
SERVICE_SSLSOAPRPC_DEFAULT = (('host','localhost.localdomain'),('port',8173),('max_children',100), ('timeout',900),('poll_interval',10),('forking',True),('daemon_threads',False), ('keyfile', 'localhost.localdomain.key'),('certfile','localhost.localdomain.crt'))

SERVICE_UDPRPC_DEFAULT = (('host','localhost.localdomain'),('port',8170),('max_children',100), ('timeout',900),('poll_interval',10),('forking',True),('daemon_threads',False))

SERVICE_UNIXRPC_DEFAULT = (('server_address','/tmp/gsrp-unixrpc'),('max_children',100), ('timeout',900),('poll_interval',10),('forking',True),('daemon_threads',False))

SERVICE_UNIXUDPRPC_DEFAULT = (('server_address','/tmp/gsrp-unixudprpc'),('max_children',100), ('timeout',900),('poll_interval',10),('forking',True),('daemon_threads',False))

SERVICE_TCPV6RPC_DEFAULT = (('host','localhost.localdomain'),('port',8170),('max_children',100), ('timeout',900),('poll_interval',10),('forking',True),('daemon_threads',False))
SERVICE_SSLTCPV6RPC_DEFAULT = (('host','localhost.localdomain'),('port',8171),('max_children',100), ('timeout',900),('poll_interval',10),('forking',True),('daemon_threads',False), ('keyfile', 'localhost.localdomain.key'),('certfile','localhost.localdomain.crt'))

SERVICE_UDPV6RPC_DEFAULT = (('host','localhost.localdomain'),('port',8170),('max_children',100), ('timeout',900),('poll_interval',10),('forking',True),('daemon_threads',False))



class configManager(object):

	CONFIG = {}

	def __init__(self, config_path):
		self.CONFIG['globals'] = dict(SERVICE_GLOBAL_DEFAULT)
		self.CONFIG['tcprpc'] = dict(SERVICE_TCPRPC_DEFAULT)
		self.CONFIG['ssltcprpc'] = dict(SERVICE_SSLTCPRPC_DEFAULT)
		self.CONFIG['soaprpc'] = dict(SERVICE_SOAPRPC_DEFAULT)
		self.CONFIG['sslsoaprpc'] = dict(SERVICE_SSLSOAPRPC_DEFAULT)
		self.CONFIG['udprpc'] = dict(SERVICE_UDPRPC_DEFAULT)
		self.CONFIG['unixrpc'] = dict(SERVICE_UNIXRPC_DEFAULT)
		self.CONFIG['unixudprpc'] = dict(SERVICE_UNIXUDPRPC_DEFAULT)
		self.CONFIG['tcpv6rpc'] = dict(SERVICE_TCPV6RPC_DEFAULT)
		self.CONFIG['ssltcpv6rpc'] = dict(SERVICE_SSLTCPV6RPC_DEFAULT)
		self.CONFIG['udpv6rpc'] = dict(SERVICE_UDPV6RPC_DEFAULT)

		cf = ConfigParser()
		cf.read(config_path)
		l = {'true':True,'false':False,'none':None, 'y': True,'yes':True, 'n': False,'no': False, 'enable':True,'disable':False}
		for s in cf.sections():
			if s.lower() in self.CONFIG:
				for (n,v) in  cf.items(s):
					if v.lower() in l:
						v = l[v.lower()]
					elif n.lower() in ('port','timeout','poll_interval','max_children'):
						v = int(v)
					if n.lower() in self.CONFIG[s]:
						if type(v) == str and len(v) > 0:
							if self.CONFIG[s][n] != v.lower():
								self.CONFIG[s][n] = v.lower()
						elif type(v) in (bool, int, None):
							if self.CONFIG[s][n] != v and v:
								self.CONFIG[s][n] = v
					else:
						_logger.info( 'Invalid parameter: - %s section: - %s - Ignored' % (n,s))
			else:
				_logger.info( 'Invalid section: - %s - Ignored' % (s,))
	def __getitem__(self,key):
		return self.CONFIG[key]

if __name__ == '__main__':
	config = configManager(opj(os.getcwd(),'conf/gsrp-connector.conf'))
	for c in ('globals','tcprpc','ssltcprpc','soaprpc','sslsoaprpc', 'udprpc','unixrpc', 'unixudprpc','tcpv6rpc','ssltcpv6rpc','udpv6rpc'):
		print("Config %s = %s" % (c,config[c]))

