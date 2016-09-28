# --*-- coding: utf-8 --*--

import sys
import traceback
import logging
import psycopg2
import psycopg2.extras
from datetime import datetime
from managers.manager import Manager
from services.cursor import Cursor
from orm.common import *
from tools.translations import trlocal as _
_logger = logging.getLogger('listener.' + __name__)

class db_exception(Exception): pass


class pgdbManager(Manager):
	"""
	Обработка данных модели
	"""
	_name = 'pgdbManager'
	_alias = 'cockroachdb'
	_inherit = 'db'
	cr = None

	def __init__(self):
		self.cr = Cursor(dsn =None, database = "system", user = "root", password = None, host = "localhost", port = 26257)
		super(pgdbManager,self).__init__()

	def login(self, dsn =None, database = None, user = None, password = None, host = None, port = None):
		return self.cr._login(dsn = dsn, database = database, user = user, password = password, host = host, port = port)

	def logout(self):
		return self.cr._logout()

	def checkLogin(self):
		return self.cr._checkLogin()

	def _setAutocommit(self, val = True):
		self.cr._setAutocommit(val = val)

	def _restoreAutocommit(self):
		self.cr._restoreAutocommit()
	
	def commit(self):
		return self.cr._commit()

	def rollback(self):
		return self.cr._rollback()
	
	def _mogrify(self, query, vars = None):
		return self.cr._mogrify(query,vars)
	
	def _execute(self, query, vars = None):
		return self.cr._execute(query, vars)
	
	def _executemany(self, query, vars_list = None):
		return self.cr._executemany(query, vars_list)
	
	def _executeList(self, query_list):
		return self.cr._executeList(query_list)
	
	def _executemanyList(self, querymany_list):
		return self.cr._executemanyList(querymany_list)
	
pgdbManager()
