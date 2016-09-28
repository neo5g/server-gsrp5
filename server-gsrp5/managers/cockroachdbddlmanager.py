# --*-- coding: utf-8 --*--

import logging
from managers.manager import Manager
from tools.translations import trlocal as _
_logger = logging.getLogger('listener.' + __name__)

class pgdbddl_exception(Exception): pass

class pgdbddlManager(Manager):
	"""
	Выполняет DDL манипуляции с реляционной базой данных POSTGRESQL 
	"""
	_name = 'pgdbddlManager'
	_alias = 'ddl'
	_inherit = 'db.cockroachdb'

	def __init__(self):
		super(pgdbddlManager,self).__init__()

	def _checkExistRole(self,rolname):
		self._dispatcher.db.pgdb._execute("SELECT count(*) FROM pg_roles WHERE rolname = %s", (rolname,))
		return self._dispatcher.db.pgdb.cr.fetchone()[0] > 0

	def listRoles(self):
		self._dispatcher.db.pgdb._execute("SELECT rolname FROM pg_roles order by rolname")
		return list(map(lambda x: x[0], self._dispatcher.db.pgdb.cr.fetchall()))


	def listsRole(self):
		self._dispatcher.db.pgdb._execute("SELECT rolname, rolsuper, rolinherit, rolcreaterole, rolcreatedb, rolcatupdate, rolreplication, rolconnlimit, to_char(rolvaliduntil,'YYYY-MM-DD HH24:MI:SS TZ') as rolvaliduntil, d.description AS comment FROM ((pg_authid AS a LEFT OUTER JOIN pg_shdescription AS d ON (d.objoid = a.oid)) LEFT OUTER JOIN pg_class AS c ON (d.classoid = c.oid AND c.relname = 'pg_authid'))")
		return self._dispatcher.db.pgdb.cr.dictfetchone()


	def getRoleAttrs(self,rolname):
		self._dispatcher.db.pgdb._execute("SELECT rolname, rolsuper, rolinherit, rolcreaterole, rolcreatedb, rolcatupdate, rolreplication, rolconnlimit, to_char(rolvaliduntil,'YYYY-MM-DD HH24:MI:SS TZ') as rolvaliduntil, d.description AS comment FROM ((pg_authid AS a LEFT OUTER JOIN pg_shdescription AS d ON (d.objoid = a.oid)) LEFT OUTER JOIN pg_class AS c ON (d.classoid = c.oid AND c.relname = 'pg_authid')) WHERE a.rolname = %s", (rolname,))
		return self._dispatcher.db.pgdb.cr.dictfetchone()

	def alterRole(self, rolname, password = None, confirm_password = None,rolsuper = False, rolinherit = False, rolcreaterole = False, rolcreatedb = False, rolcatupdate = False, rolreplication = False, rolconnlimit = -1, rolvaliduntil = 'infinity', comment = None):
		_locals = locals()
		self._dispatcher.db.pgdb.cr._setAutocommit()
		if not self._checkExistRole(rolname):
			self._dispatcher.db.pgdb.cr._restoreAutocommit()
			return [1,_(u'Role %s is not exist') % (rolname,)]
		_attrs = {'rolsuper': {True:' SUPERUSER',False:' NOSUPERUSER'},'password':" ENCRYPTED PASSWORD %s",'rolinherit':{True:' INHERIT',False:' NOINHERIT'},'rolcreatedb':{True:' CREATEDB',False:' NOCREATEDB'},'rolcreaterole':{True:'  CREATEROLE',False:' NOCREATEROLE'},'rolreplication':{True:' REPLICATION',False:' NOREPLICATION'},'rolconnlimit':" CONNECTION LIMIT %s",'rolvaliduntil':" VALID UNTIL '%s'"}
		_rolAttrs = self.getRoleAttrs(rolname)
		_sqls = []
		_sql = "ALTER ROLE "+rolname
		_rolchange = False
		for key in _locals.keys():
			if key in ('self', 'rolname','rolcatupdate' ,'comment','confirm_password'):
				continue
			if key == 'password':
				if _locals[key]:
					_sql += _attrs[key] % (_locals[key],)
				continue
			if _locals[key] != _rolAttrs[key]:
				if key in ('rolconnlimit', 'rolvaliduntil'):
					_sql += _attrs[key] % (_locals[key],)
				else:
					_sql += _attrs[key][_locals[key]]
				_rolchange = True
		if _rolchange:
			_sqls.append([_sql,None])

		if _locals['rolsuper']:
			if _locals['rolcatupdate']:
				if _locals['rolcatupdate'] != _rolAttrs['rolcatupdate']:
					_sqls.append(["UPDATE pg_authid SET rolcatupdate=true WHERE rolname=%s", (_locals['rolname'],)])
					_sqls.append(_sql)
			else:
				if _locals['rolcatupdate'] != _rolAttrs['rolcatupdate']:
					_sqls.append(["UPDATE pg_authid SET rolcatupdate=false WHERE rolname=%s", (_locals['rolname'],)])

		if comment:
			if _rolAttrs['comment']:
				if _rolAttrs['comment'] != comment:
					_sqls.append(["COMMENT ON ROLE "+rolname+" IS %s", (comment,)])
			else:
				_sqls.append(["COMMENT ON ROLE "+rolname+" IS %s", (comment,)])
		else:
			if _rolAttrs['comment']:
				_sqls.append(["COMMENT ON ROLE "+rolname+" IS %s", ('',)])

		if _sqls.__len__() > 0:
			self._dispatcher.db.pgdb.cr._executeList(_sqls)
			_logger.info("ALTER ROLE %s" % (_locals['rolname'],))
			self._dispatcher.db.pgdb.cr._restoreAutocommit()
			return [True, _("Role %s was altered") % (_locals['rolname'],)]
		else:
			self._dispatcher.db.pgdb.cr._restoreAutocommit()
			return [True, _("Role %s not changed") % (_locals['rolname'],)]


	def createRole(self, rolname, password = None, confirm_password = None,rolsuper = False, rolinherit = False, rolcreaterole = False, rolcreatedb = False, rolcatupdate = False, rolreplication = False, rolconnlimit = -1, rolvaliduntil = 'infinity', comment = None):
		self._dispatcher.db.pgdb.cr._setAutocommit()
		if self._checkExistRole(rolname):
			self._dispatcher.db.pgdb.cr._restoreAutocommit()
			return [1,_('Role %s is exist') % (rolname,)]
		_sqls = []
		_sql = "CREATE ROLE %s LOGIN ENCRYPTED PASSWORD '%s' " % (rolname, password)
		if rolsuper:
			_sql += ' SUPERUSER'
		if rolinherit:
			_sql += ' INHERIT'
		else:
			_sql += ' NOINHERIT'
		if rolcreatedb:
			_sql += ' CREATEDB'
		if rolcreaterole:
			_sql += ' CREATEROLE'
		if rolreplication:
			_sql += ' REPLICATION'
		if rolvaliduntil.__len__() == 0:
				rolvaliduntil = 'infinity'
		_sql += " VALID UNTIL '%s'" % (rolvaliduntil,)
		_sql += ' CONNECTION LIMIT %s' % (rolconnlimit,)
		_sqls.append(_sql)
		print('SQL', _sql)
		if comment and comment.__len__() > 0:
			_sql = "COMMENT ON ROLE %s IS '%s'" % (rolname,comment)
			_sqls.append(_sql)
		if rolsuper:
			if rolcatupdate:
				_val = 'true'
			else:
				_val = 'false'
			_sql = "UPDATE pg_authid SET rolcatupdate=%s WHERE rolname='%s'" % (_val,rolname)
			_sqls.append(_sql)
		self._dispatcher.db.pgdb.cr._executeList(_sqls)
		_logger.info("CREATE ROLE %s" % (rolname,))
		self._dispatcher.db.pgdb.cr._restoreAutocommit()
		return [True, _("Role %s was creared") % (rolname,)]

	def dropRole(self, rolname):
		self._dispatcher.db.pgdb.cr._setAutocommit()
		if not self._checkExistRole(rolname):
			self._dispatcher.db.pgdb.cr._restoreAutocommit()
			return [2,_('Role %s is not exist') % (rolname,)]
		self._dispatcher.db.pgdb.cr._execute('DROP ROLE %s' % (rolname,))
		_logger.info("DROP ROLE %s" % (rolname,))
		self._dispatcher.db.pgdb.cr._restoreAutocommit()
		return [True, _("Role %s was droped") % (rolname,)]

# Tablespace

	def _checkExistTablespace(self,spcname):
		self._dispatcher.db.pgdb.cr._execute("SELECT count(*) FROM pg_tablespace WHERE spcname = %s", (spcname,))
		return self._dispatcher.db.pgdb.cr.fetchone()[0] > 0

	def listTablespaces(self):
		self._dispatcher.db.pgdb.cr._execute("SELECT spcname FROM pg_tablespace order by spcname")
		return list(map(lambda x: x[0], self._dispatcher.db.pgdb.cr.fetchall()))

	def getTablespaceAttrs(self,spcname):
		self._dispatcher.db.pgdb.cr._execute("SELECT spcname, auth.rolname as owner, pg_tablespace_location(t.oid) as location, d.description AS comment FROM (((pg_tablespace as t INNER JOIN pg_authid as auth on (t.spcowner = auth.oid)) LEFT OUTER JOIN pg_shdescription AS d ON (d.objoid = t.oid)) LEFT OUTER JOIN pg_class AS c ON (d.classoid = c.oid AND c.relname = 'pg_tablespace')) WHERE t.spcname = %s", (spcname,))
		return self._dispatcher.db.pgdb.cr.dictfetchone()


	def alterTablespace(self, spcname, location, owner, comment = None):
		self._dispatcher.db.pgdb.cr._setAutocommit()
		if not self._checkExistTablespace(spcname):
			self._dispatcher.db.pgdb.cr._restoreAutocommit()
			return [1,'Tablespace %s is not exist' % (spcname,)]
		_sqls = []
		_tablespacechange = False
		_sql = "ALTER TABLESPACE %s" % (spcname,)
		_tablespaceAttrs = self.getTablespaceAttrs(spcname)
		if owner != _tablespaceAttrs['owner']:
			_sql += " OWNER TO %s" % (owner,)
			_tablespacechange = True
		if _tablespacechange:
			_sqls.append([_sql, None])
		if comment != _tablespaceAttrs['comment']:
			_sql = "COMMENT ON TABLESPACE %s IS '%s'" % (spcname,comment)
			_sqls.append([_sql, None])
		if _sqls.__len__() > 0:
			self._dispatcher.db.pgdb.cr._executeList(_sqls)
			_logger.info("ALTER TABLESPACE %s" % (spcname,))
			self._dispatcher.db.pgdb.cr._restoreAutocommit()
			return [True, _("Tablespace %s was altered") % (spcname,)]
		else:
			return [True, _("Tablespace %s not changed") % (spcname,)]

	def createTablespace(self, spcname, owner = None, location = None, comment = None):
		self._dispatcher.db.pgdb.cr._setAutocommit()
		if self._checkExistTablespace(spcname):
			self._dispatcher.db.pgdb.cr._restoreAutocommit()
			return [1, _('Tablespace %s is exist') % (spcname,)]
		_sqls = []
		_sql = "CREATE TABLESPACE %s" % (spcname, )
		if owner:
			_sql += " OWNER %s" % (owner,)
		if location:
			_sql += " LOCATION '%s'" % (location,)
		_sqls.append([_sql, None])
		if comment:
			_sql = "COMMENT ON TABLESPACE %s IS '%s'" % (spcname,comment)
			_sqls.append([_sql, None])
		self._dispatcher.db.pgdb.cr._executeList(_sqls)
		_logger.info("CREATE TABLESPACE %s" % (spcname,))
		self._dispatcher.db.pgdb.cr._restoreAutocommit()
		return [True, _("Tablespace %s was created") % (spcname,)]

	def dropTablespace(self, spcname):
		self._dispatcher.db.pgdb.cr._setAutocommit()
		if not self._checkExistTablespace(spcname):
			self._dispatcher.db.pgdb.cr._restoreAutocommit()
			return [2, _('Tablespace %s is not exist') % (spcname,)]
		self._dispatcher.db.pgdb.cr._execute('DROP TABLESPACE %s' % (spcname,))
		self._dispatcher.db.pgdb.cr._restoreAutocommit()
		_logger.info("DROP TABLESPACE %s" % (spcname,))
		return [True, _("Tablespace %s was droped") % (spcname,)]
# Database
	def _checkExistDatabase(self,datname):
		self._dispatcher.db.pgdb.cr._execute("SELECT count(*) FROM pg_database WHERE datname = %s", (datname,))
		return self._dispatcher.db.pgdb.cr.fetchone()[0] > 0

	def listDatabases(self):
		self._dispatcher.db.pgdb.cr._execute("SELECT datname FROM pg_database order by datname")
		return list(map(lambda x: x[0], self._dispatcher.db.pgdb.cr.fetchall()))

	def getDatabaseAttrs(self,datname):
		self._dispatcher.db.pgdb.cr._execute("SELECT datname, pg_encoding_to_char(encoding) as encoding, auth.rolname as owner,datcollate as lc_collate, datctype as lc_ctype, datconnlimit as datconnlimit, t.spcname as spcname,d.description AS comment FROM (((pg_database AS p INNER JOIN pg_tablespace as t on (p.dattablespace = t.oid) INNER JOIN pg_authid as auth on (p.datdba = auth.oid)) LEFT OUTER JOIN pg_shdescription AS d ON (d.objoid = p.oid)) LEFT OUTER JOIN pg_class AS c ON (d.classoid = c.oid AND c.relname = 'pg_database')) WHERE p.datname = %s", (datname,))
		return self._dispatcher.db.pgdb.cr.dictfetchone()

	def alterDatabase(self,datname, owner, datconnlimit, spcname, comment=None, encoding=None,newdatname = None,):
		"""
		ALTER DATABASE q2
		  RENAME TO q21;
		ALTER DATABASE q21
		  OWNER TO q1234567;
		COMMENT ON DATABASE q21
		  IS 'qwerty23';
		ALTER DATABASE q21
		  SET TABLESPACE pg_default;
		ALTER DATABASE q21
		  WITH CONNECTION LIMIT = 5;
		"""
		self._dispatcher.db.pgdb.cr._setAutocommit()
		if not self._checkExistDatabase(datname):
			self._dispatcher.db.pgdb.cr._restoreAutocommit()
			return [2, _('Database %s is not exist') % (datname,)]
		_dbchange = False
		_sqls = []
		_dbAttrs = self.getDatabaseAttrs(datname)
		if newdatname and datname !=  newdatname:
			_sql = "ALTER DATABASE %s RENAME to %s" % (datname, newdatname)
			_sqls.append([_sql, None])
			datname = newdatname		
		if owner != _dbAttrs['owner']:
			_sql = "ALTER DATABASE %s OWNER TO %s" % (datname, owner)
			_sqls.append([_sql, None])
		if datconnlimit != _dbAttrs['datconnlimit']:
			_sql = "ALTER DATABASE %s WITH CONNECTION LIMIT %s" % (datname, datconnlimit)
			_sqls.append([_sql, None])
		if spcname != _dbAttrs['spcname']:
			_sql = "ALTER DATABASE %s SET TABLESPACE %s" % (datname, spcname)
			_sqls.append([_sql, None])
		if comment != _dbAttrs['comment']:
			_sql = "COMMENT ON DATABASE %s IS '%s'" % (datname, comment)
			_sqls.append([_sql, None])
		if len(_sqls) > 0:
			self._dispatcher.db.pgdb.cr._executeList(_sqls)
			self._dispatcher.db.pgdb.cr._restoreAutocommit()
			_logger.info(_("ALTER DATABASE %s") % (datname,))
			return [True, _("Database %s was atered") % (datname,)]
		else:
			self._dispatcher.db.pgdb.cr._restoreAutocommit()
		return [True, _("Database %s not changed") % (datname,)]


	def createDatabase(self, datname, encoding = None, owner = None, template = None, lc_collate = None, lc_ctype = None, datconnlimit = -1, spcname = None, comment = None):
		self._dispatcher.db.pgdb.cr._setAutocommit()
		if self._checkExistDatabase(datname):
			self._dispatcher.db.pgdb.cr._restoreAutocommit()
			return [1, _('Database %s is exist') % (datname,)]
		_sqls = []
		_sql = "CREATE DATABASE %s" %(datname,)
		if encoding:
			_sql += " WITH ENCODING '%s'" % (encoding,)
		if owner:
			_sql += " OWNER %s" % (owner,)
		if template:
			_sql += " TEMPLATE %s" % (template,)
		if lc_collate:
			_sql += " LC_COLLATE '%s'" % (lc_collate,)
		if lc_ctype:
			_sql += " LC_CTYPE '%s'" % (lc_ctype,)
		if datconnlimit != -1:
			_sql += " CONNECTION LIMIT %s" % (datconnlimit,)
		if spcname:
			_sql += " TABLESPACE %s" % (spcname,)
		_sqls.append([_sql, None])
		if comment:
			_sql = "COMMENT ON DATABASE %s IS '%s'" % (datname,comment)
			_sqls.append([_sql, None])
		rc = self._dispatcher.db.pgdb.cr._executeList(_sqls)
		self._dispatcher.db.pgdb.cr._restoreAutocommit()
		_logger.info("CREATE DATABASE %s" % (datname,))
		return [True, _("Database %s was created") % (datname,)]

	def dropDatabase(self,datname):
		self._dispatcher.db.pgdb.cr._setAutocommit()
		if not self._checkExistDatabase(datname):
			self._dispatcher.db.pgdb.cr._restoreAutocommit()
			return [2, _('Database %s is not exist') % (datname,)]
		self._dispatcher.db.pgdb.cr._execute('DROP DATABASE %s' % (datname,))
		self._dispatcher.db.pgdb.cr._restoreAutocommit()
		_logger.info("DROP DATABASE %s" % (datname,))	
		return [True, _("Database %s was droped") % (datname,)]

# Schema
	def _checkExistSchema(self,nspname):
		self._dispatcher.db.pgdb.cr._execute("SELECT count(*) FROM pg_namespace WHERE nspname = %s", (nspname,))
		return self._dispatcher.db.pgdb.cr.fetchone()[0] > 0

	def getSchemaAttrs(self,nspname):
		self._dispatcher.db.pgdb._execute("select a.nspname,b.rolname as owner,d.description as comment from (pg_namespace as a inner join pg_authid as b on(a.nspowner=b.oid) left outer join pg_description as d on(a.oid=d.objoid)) LEFT OUTER JOIN pg_class AS c ON (d.classoid = c.oid AND c.relname = 'pg_namespace') WHERE a.nspname = %s", (nspname,))
		return self._dispatcher.db.pgdb.cr.dictfetchone()

	def listSchemas(self):
		self._dispatcher.db.pgdb.cr._execute("SELECT nspname FROM pg_namespace where nspname not in ('pg_catalog','pg_toast','public','pg_temp_1','pg_toast_temp_1','information_schema') order by nspname")
		return list(map(lambda x: x[0], self._dispatcher.db.pgdb.cr.fetchall()))

	def alterSchema(self, nspname, owner, newnspname = None, comment = None):
		"""ALTER SCHEMA <nspname> OWNER TO <owner>;
		COMMENT ON SCHEMA <nspname> IS '<comment>';"""
		self._dispatcher.db.pgdb.cr._setAutocommit()
		if not self._checkExistSchema(nspname):
			self._dispatcher.db.pgdb.cr._restoreAutocommit()
			return [2, _('Schema %s is not exist') % (nspname,)]
		_schchange = False
		_sqls = []
		_dbAttrs = self.getSchemaAttrs(nspname)
		if newnspname and nspname !=  newnspname:
			_sql = "ALTER SCHEMA %s RENAME to %s" % (nspname, newnspname)
			_sqls.append([_sql, None])
			nspname = newnspname		
		if owner != _dbAttrs['owner']:
			_sql = "ALTER SCHEMA %s OWNER TO %s" % (nspname, owner)
			_sqls.append([_sql, None])
		if comment and comment != _dbAttrs['comment']:
			_sql = "COMMENT ON SCHEMA %s IS '%s'" % (nspname, comment)
			_sqls.append([_sql, None])
		if len(_sqls) > 0:
			self._dispatcher.db.pgdb.cr._executeList(_sqls)
			self._dispatcher.db.pgdb.cr._restoreAutocommit()
			_logger.info(_("ALTER SCHEMA %s") % (nspname,))
			return [True, _("Schema %s was atered") % (nspname,)]
		else:
			self._dispatcher.db.pgdb.cr._restoreAutocommit()
		return [True, _("Schema %s not changed") % (nspname,)]

	def createSchema(self, nspname, owner= None, comment = None):
		"""CREATE SCHEMA <nspname> AUTHORIZATION <owner>;
			COMMENT ON SCHEMA <nspname> IS '<comment>';"""
		self._dispatcher.db.pgdb.cr._setAutocommit()
		if self._checkExistSchema(nspname):
			self._dispatcher.db.pgdb.cr._restoreAutocommit()
			return [1, _('Schema %s is exist') % (nspname)]
		_sqls = []
		_sql = "CREATE SCHEMA %s" %(nspname,)
		if owner:
			_sql += " AUTHORIZATION %s" % (owner,)
		_sqls.append(_sql)
		if comment:
			_sql = "COMMENT ON SCHEMA %s IS '%s'" % (nspname,comment)
			_sqls.append([_sql, None])
		rc = self._dispatcher.db.pgdb.cr._executeList(_sqls)
		self._dispatcher.db.pgdb.cr._restoreAutocommit()
		_logger.info("CREATE SCHEMA %s" % (nspname,))
		return [True, _("Schema %s was created") % (nspname,)]

		pass

	def dropSchema(self,nspname):
		"""DROP SCHEMA <nspname>"""
		self._dispatcher.db.pgdb.cr._setAutocommit()
		if not self._checkExistSchema(nspname):
			self._dispatcher.db.pgdb.cr._restoreAutocommit()
			return [2, _('Schema %s is not exist') % (nspname)]
		self._dispatcher.db.pgdb.cr._execute('DROP SCHEMA %s' % (nspname,))
		self._dispatcher.db.pgdb.cr._restoreAutocommit()
		_logger.info("DROP SCHEMA %s" % (nspname,))
		return [True, _("Schema %s was droped") % (nspname,)]

pgdbddlManager()

