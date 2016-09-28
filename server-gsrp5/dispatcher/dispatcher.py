# --*-- coding: utf-8 --*--

import sys
import logging
from functools import reduce
from modules.registry import Registry,infoModule
from tools.translations import trlocal as _

_logger = logging.getLogger('listener.' + __name__)

class Dispatcher(object):

	_db_logged_in = None
	_db_logged_kwargs = {}
	_logged_in = None
	_logged_in_kwargs = {}

	def _isdbLogged(self):
		return self._self._db_logged_in

	def _setdbLogin(self, kwargs):
		if not self._db_logged_in:
			self._db_logged_in = True
			self._db_logged_in_kwargs = kwargs

	def _getdbLogin(self):
		return (self._db_logged_in, self._db_logged_in_kwargs)


	def _setdbLogout(self):
		if self._db_logged_in:
			self._db_logged_in = False
			self._db_logged_in_kwargs = {}

	def _isLogged(self):
		return self._self._logged_in

	def _setLogin(self, kwargs):
		if not self._logged_in:
			self._logged_in = True
			self._logged_in_kwargs = kwargs

	def _getLogin(self):
		return (self._logged_in, self.logged_in_kwargs)


	def _setLogout(self):
		if self._logged_in:
			self._logged_in = False
			self._logged_in_kwargs = {}

	def _dispatch(self, args, kwargs = None):
		keys = args[0].split('.')
		method = getattr(self, args[0], getattr(self,keys[0]))
		#print('METHOD:',method)
		if method == getattr(self,keys[0]):
			method._name = args[0]
		if len(args) == 1:
			if kwargs and len(kwargs) > 0:
				return method(**(kwargs))
			else:
				return method()
		elif len(args) > 1:
			if kwargs and len(kwargs) > 0:
				return method(*((args[1:])),**(kwargs))
			else:
				return method(*((args[1:])))

	def __init__(self, managers, gsrp_root = None):
		keys = list(map(lambda x: x.split('.'), list(managers.keys())))
		keys.sort(key=len)
		for key in keys:
			m = self
			for k in key:
				attr = getattr(m, k, None)
				if attr:
					m = attr
					continue
				else:
					name = reduce(lambda x,y: x + '.' + y, key)
					setattr(m , k, managers[name].create_instance(self))
					#setattr(getattr(m, k, None),'_dispatcher', self)
					#setattr(getattr(m, k, None),'_dispatch', self._dispatch)
		
		self.db._switch['db']['cockroachdb'] = self.db.cockroachdb
		self._registry = Registry(self,gsrp_root)
		
	def _execute(self, args, kwargs = None):
		return self._dispatch(args, kwargs)




