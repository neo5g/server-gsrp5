# --*-- coding: utf-8 --*--

from flask import jsonify
from local.manager import Manager

class dbauthManager(Manager):
	"""
	Выполняет манипуляции с реляционной базой данных POSTGRESQL
	"""
	_name = 'dbauthManager'
	_alias = 'auth'
	_inherit = 'app.db'

	def Login(self, **kwargs):
		if self._dispatcher._db_logged_in:
			res = [self._dispatcher._db_logged_in, 'Your a logged as %s' % self._dispatcher._db_logged_kwargs['user']]
		else:
			res = self._dispatcher._dispatch(['db.db.login'],kwargs)
			if res[0]:
				self._dispatcher._setdbLogin(kwargs)
		return jsonify({'json': res})

	def Logout(self):
		if self._dispatcher._db_logged_in:
			res = self._dispatch(['db.db.logout'])
		else:
			res = [self._dispatcher._db_logged_in, 'Your a as not logged in']
		return jsonify({'json': res})

dbauthManager()
