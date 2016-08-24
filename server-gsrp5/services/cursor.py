# --*-- coding: utf-8 --*--

import psycopg2
import psycopg2.extras
from psycopg2 import Error
from tools.translations import trlocal as _

class Cursor(object):
	conn = None
	cr = None
	def _connect(self, dsn, database, user, password, host, port):
		if self.conn:
			if self.conn.closed:
				self.conn = psycopg2.connect(dsn = self.dsn, database = self.database, user = self.user, password = self.password, host = self.host, port = self.port, connection_factory = psycopg2.extensions.connection)
			else:
				return True
		else:
			self.dsn = dsn
			self.database = database
			self.user = user
			self.password = password
			self.host = host
			self.port = port
			self.conn = psycopg2.connect(dsn = self.dsn, database = self.database, user = self.user, password = self.password, host=self.host, port=self.port, connection_factory = psycopg2.extensions.connection)
			#self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED)
			return True

	def _cursor(self):
		if self.conn:
			if self.cr and not self.cr.closed:
				return True
			else:
				#self.cr = self.conn.cursor(cursor_factory = psycopg2.extras.NamedTupleCursor)
				self.cr = self.conn.cursor()
				return True
		else:
			return False

	def _checkLogin(self):
		return self.conn and self.cr and not self.conn.closed and not self.cr.closed

	def _setAutocommit(self, val = True):
		if self.conn and  not self.conn.closed and self.cr and not self.cr.closed:
			self._isolation_level = self.conn.isolation_level
			self.conn.set_isolation_level(0)
			self._autocommit = self.conn.autocommit
			if self.conn.autocommit != val:
				self.conn.autocommit = val

	def _restoreAutocommit(self):
		if self.conn and  not self.conn.closed and self.cr and not self.cr.closed:
			if self.conn.autocommit != self._autocommit:
				self.conn.set_isolation_level(self._isolation_level)
				self.conn.autocommit = self._autocommit

	def _mogrify(self, query, vars):
		return self.cr.mogrify(query,vars)

	def _execute(self, query, vars = None):
		try:
			#print('QUERY:',query,'VARS:',vars)
			self.cr.execute(query = query, vars = vars)
			#print('STATUS MESSAGE:',self.cr.statusmessage)
		except:
			print('Error cursor')
			self._rollback()
			raise
	
	def _executemany(self, query, vars_list):
		try:
			self.cr.execute(query = query, vars_list = vars_list)
		except:
			self._rollback()
			raise
	
	def _executeList(self, query_list):
		try:
			for q in query_list:
				#print('TYPE',type(q),query_list)
				if type(q) in (tuple,list):
					query = q[0]
					vars = q[1]
				elif type(q) in (str,bytes):
					query = q
					vars = None				
			#for query, vars in query_list:
				#print('QUERY VARS:',query,vars)
				self.cr.execute(query = query, vars = vars)
		except:
			print('Error cursor')
			self._rollback()
			raise
	def _executemanyList(self, querymany_list):
		try:
			for query, vars_list in querymany_list:
				self.cr.execute(query = query, vars_list = vars_list)
		except:
			self._rollback()
			raise

	def _commit(self):
		if self.conn and not self.conn.closed:
			self.conn.commit()
			return True
		else:
			return False

	def _rollback(self):
		if self.conn and not self.conn.closed:
			self.conn.rollback()
			return True
		else:
			return False

	def fetchone(self):
		if self.cr.rowcount > 0:
			r = self.cr.fetchone()
			#print('RESULT FETCHONE:',r)
			return r
			#return self.cr.fetchone()
		return {}
		#else:
			#print('FETCH ONE:',self.cr.rowcount)

	def dictfetchone(self):
		record = {}
		if self.cr.rowcount > 0:
			row = self.cr.fetchone()
			for i in range(self.cr.description.__len__()):
				record[self.cr.description[i].name] = row[i]
		return record

	def fetchmany(self, size = None):
		if not size:
			size = self.cr.arraysize
		return self.cr.fetchmany(size = size)

	def dictfetchmany(self, size = None):
		if not size:
			size = self.cr.arraysize
		records = []
		if self.cr.rowcount > 0:
			for row in self.cr.fetchmany(size=size):
				record = {}
				for i in range(self.cr.description.__len__()):
					record[self.cr.description[i].name] = row[i]
				records.append(record)
		return records

	def fetchall(self):
		return self.cr.fetchall()

	def dictfetchall(self):
		records = []
		if self.cr.rowcount > 0:
			for row in self.cr.fetchmany(size=size):
				record = {}
				for i in range(self.cr.description.__len__()):
					record[self.cr.description[i].name] = row[i]
				records.append(record)
		return records


	def _login(self,dsn, database, user, password, host, port):
		if self._checkLogin() or (self._connect(dsn = dsn, database = database, user = user, password = password, host = host, port = port) and self._cursor()):
			return [True,_("You logged as %s") % (user,)]
		else:
			return [False, _("You a not logged. Invalid username or password")]

	def _logout(self):
		if self.cr and not self.cr.closed:
			self.cr.close()
			self.cr = None
		if self.conn and not self.conn.closed:
			self.conn.close()
			self.conn = None
			return [True, _("User %s is logout") % (self.user,)]
		else:
			return [False, _("You a not logged")]
