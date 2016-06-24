# --*-- coding: utf-8 --*--

import sys
import logging

_logger = logging.getLogger(__name__)

class Dispatcher(object):

	_db_logged_in = None
	_db_loggin_kwargs = {}
	_logged_in = None
	_logged_in_kwargs = {}

	def _setdbLogin(self, kwargs):
		if self._db_logged_in:
			self._db_logged_in = True
			self._db_logged_in_kwargs = kwargs

	def _getdbLogin(self):
		return (self._db_logged_in, self._db_logged_in_kwargs)


	def _setdbLogout(self):
		if self._db_logged_in:
			self._db_logged_in = False
			self._db_logged_in_kwargs = {}

	def _setLogin(self, kwargs):
		if self._logged_in:
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
		method = self
		for key in keys:
			method = getattr(method,key,None)
		if len(args[1:]) > 0:
			if kwargs and len(kwargs) > 0:
				return method(*((args[1:])),**(kwargs))
			else:
				return method(*((args[1:])))
		else:
			if kwargs and len(kwargs) > 0:
				return method(**(kwargs))
			else:
				return method()


	def __init__(self, managers):
		keys = map(lambda x: x.split('.'), managers.keys())
		keys.sort(cmp = lambda x,y: cmp(len(x),len(y)))
		for key in keys:
			m = self
			for k in key:
				attr = getattr(m, k, None)
				if attr:
					m = attr
					continue
				else:
					name = reduce(lambda x,y: x + '.' + y, key)
					setattr(m , k, managers[name].create_instance())
					setattr(getattr(m, k, None),'_dispatcher', self)
					setattr(getattr(m, k, None),'_dispatch', self._dispatch)

	def _execute(self, args, kwargs = None):
		return self._dispatch(args, kwargs)




