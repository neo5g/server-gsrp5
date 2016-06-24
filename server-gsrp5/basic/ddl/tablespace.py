# -*- coding: utf-8 -*-

from functools import reduce
from collections import OrderedDict
from orm import fields
from orm.model import TransientModel

class ddl_model_tablespace(TransientModel):
	_name = 'ddl.model.tablespace'
	_description = 'Database Role'
	_columns  = OrderedDict([
	('oid',fields.integer(label = 'Oid')),
	('spcname',fields.varchar(label = 'Spcname',size=64)),
	('owner',fields.varchar(label = 'Owner', size=64)),
	('location',fields.varchar(label = 'Location',size=255)),
	('comment', fields.text(label = 'Comment'))
	])
	
	def create(self, vals):
		return self._dba._modelCreate(self,vals) 

	def search(self, where):
		return self._dba._modelSearch(self,where) 

	def read(self, ids, fields = None):
		_sqls = []
		_sql = "SELECT t.oid as oid, spcname, auth.rolname as owner, pg_tablespace_location(t.oid) as location, d.description AS comment FROM (((pg_tablespace as t INNER JOIN pg_authid as auth on (t.spcowner = auth.oid)) LEFT OUTER JOIN pg_shdescription AS d ON (d.objoid = t.oid)) LEFT OUTER JOIN pg_class AS c ON (d.classoid = c.oid AND c.relname = 'pg_tablespace')) WHERE t.oid in (%s)"
		var = reduce(lambda x,y: str(x)+','+str(y), ids)
		_sqls.append([_sql, var])
		return self._dispatcher.app.db.cr.dictfetchone()



	def write(self, vals):
		return self._dba._modelWrite(self,vals) 

	def unlink(self, ids):
		return self._dba._modelUnlink(self,ids) 


ddl_model_tablespace()

