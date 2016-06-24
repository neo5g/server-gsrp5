# -*- coding: utf-8 -*-

from functools import reduce
from collections import OrderedDict
from orm import fields
from orm.model import TransientModel

class ddl_model_schema(TransientModel):
	_name = 'ddl.model.schema'
	_description = 'Database Schemas'
	_recname = "nspname"
	_columns = OrderedDict([
	('nspname', fields.varchar(label = 'Nspname',size=64 ,selectable=True,filtering=[('not like','pg_%'),('!=','information_schema'),('!=','public')],domain=[('nspname','like','%')])),
	('owner', fields.varchar(label = 'Owner',size=64)),
	('comment', fields.text(label = 'Comment'))
	])

		
	def create(self,model, vals, context = {}):
		raise NotImplemented

	def write(self, vals, context = {}):
		raise NotImplemented

	def unlink(self, model, ids, context = {}):
		raise NotImplemented
	
	def _checkExistSchema(self,nspname):
		self._dispatcher.app.db.cr._execute("SELECT count(*) FROM pg_namespace WHERE nspname = %s", (nspname,))
		return self._dispatcher.app.db.cr.fetchone()[0] > 0

	def listSchemas(self):
		self._dispatcher.app.db.cr._execute("SELECT nspname FROM pg_namespace where nspname not in ('pg_catalog','pg_toast','public','pg_temp_1','pg_toast_temp_1','information_schema') order by nspname")
		return list(map(lambda x: x[0], self._dispatcher.app.db.cr.fetchall()))

	
	def _getSchemaAttrs(self,nspname):
		self._dispatcher.app.db._execute("select a.nspname,b.rolname as owner,d.description as comment from (pg_namespace as a inner join pg_authid as b on(a.nspowner=b.oid) left outer join pg_description as d on(a.oid=d.objoid)) LEFT OUTER JOIN pg_class AS c ON (d.classoid = c.oid AND c.relname = 'pg_namespace') WHERE a.nspname = %s", (nspname,))
		return self._dispatcher.app.db.cr.dictfetchone()


	def rename(self,oldnspname,newnspname):
		if newnspname == oldnspname:
			return [3, _('New name of schema equal to old name: (%s == %s)') % (newnspname, oldnspname)]

		if self._checkExistSchema(newnspname):
			self._dispatcher.app.db.cr._restoreAutocommit()
			return [1, _('Schema %s is exist') % (newnspname,)]

		self._dispatcher.app.db.cr._setAutocommit()
		if not self._checkExistSchema(oldnspname):
			self._dispatcher.app.db.cr._restoreAutocommit()
			return [2, _('Schema %s is not exist') % (oldnspname,)]

		_sqls = []
		_sql = "ALTER SCHEMA %s RENAME to %s" % (nspname, newnspname)
		_sqls.append([_sql, None])
		self._dispatcher.app.db.cr._executeList(_sqls)
		self._dispatcher.app.db.cr._restoreAutocommit()
		_logger.info(_("RENAME SCHEMA %s TO %s") % (oldnspname,newnspname))
		return [True, _("Schema %s was renamed to %s") % (oldnspname,newnspname)]

	def alterSchema(self, nspname, owner, comment = None):
		"""ALTER SCHEMA <nspname> OWNER TO <owner>;
		COMMENT ON SCHEMA <nspname> IS '<comment>';"""
		self._dispatcher.app.db.cr._setAutocommit()
		if not self._checkExistSchema(nspname):
			self._dispatcher.app.db.cr._restoreAutocommit()
			return [2, _('Schema %s is not exist') % (nspname,)]
		_sqls = []
		_dbAttrs = self._getSchemaAttrs(nspname)
		if owner != _dbAttrs['owner']:
			_sql = "ALTER SCHEMA %s OWNER TO %s" % (nspname, owner)
			_sqls.append([_sql, None])
		if comment and comment != _dbAttrs['comment']:
			_sql = "COMMENT ON SCHEMA %s IS '%s'" % (nspname, comment)
			_sqls.append([_sql, None])
		if len(_sqls) > 0:
			self._dispatcher.app.db.cr._executeList(_sqls)
			self._dispatcher.app.db.cr._restoreAutocommit()
			_logger.info(_("ALTER SCHEMA %s") % (nspname,))
			return [True, _("Schema %s was atered") % (nspname,)]
		else:
			self._dispatcher.app.db.cr._restoreAutocommit()
		return [True, _("Schema %s not changed") % (nspname,)]
		
		
		
ddl_model_schema()
