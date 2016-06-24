# --*-- coding: utf-8 --*--

import logging
from managers.manager import Manager
from orm.common import *
from tools.translations import trlocal as _
_logger = logging.getLogger('listener.' + __name__)

class pgdb_exception(Exception): pass

class pgdbmodelManager(Manager):
	"""
	Выполняет манипуляции с реляционной базой данных POSTGRESQL
	"""
	_name = 'pgdbmodelManager'
	_alias = 'model'
	_inherit = 'db.pgdb'

	def __init__(self):
		super(pgdbmodelManager,self).__init__()

# Build models - Start
	def _log_access_columns(self, model, user_sql_schema = 'tst.'):
		_r = ''
		if model._log_access:
			for f,t in LOG_ACCESS_COLUMNS.items():
				if f == "create_uid" or f == "write_uid":
					_r += ', ' + f + ' ' + (t % user_sql_schema)
				else:
					_r += ', ' + f + ' ' + t
		return _r

	def _get_column_name(self, model, name):
		if name not in MAGIC_COLUMNS:
			if name.islower() and name not in SQL_RESERVED_KEYWORDS:
				l = ''
			else:
				l = '"'
		else:
			raise (ColumnNameError, name)
		return l+name+l

	def _get_column_type(self, model, name):
		db_type = model._columns[name]._db_type
		if db_type:
			return ' ' + db_type
		else:
			return db_type

	def _get_column_size(self, model, name):
		t = model._columns[name]._type
		if t in ('char','varchar','selection'):
			if model._columns[name].size:
				_s = '('+str(model._columns[name].size)+')'
			else:
				_s = ''
		elif t in ('float','decimal','numeric'):
			_s = str(model._columns[name].size)
		else:
			_s = ''
		return _s

	def _get_column_constraints(self, model, name):
		_c = ''
		column = model._columns[name]
		if hasattr(column,'required') and column.required:
			_c += ' NOT NULL'
		if column._type in ('many2one','related','state'):
			_c += ' REFERENCES ' +  self._get_schema_name(model) + column.obj.replace('.','_') + ' (id)'
		if hasattr(column,'on_delete') and column.on_delete != None:
			_c += ' ON DELETE'+ RESTRCT_TYPE_DB.get(column.on_delete.lower(), ' NO ACTION')
		if hasattr(column,'on_update') and column.on_update != None:
			_c += ' ON UPDATE'+ RESTRCT_TYPE_DB.get(column.on_update.lower(), ' NO ACTION')
		if name == model._rec_name or hasattr(column,'unique') and column.unique:
			_c += ' UNIQUE'
		if hasattr(column,'check') and column.check != None:
			_c += ' CHECK ('+ column.check +')'
		return _c

	def _model_table_columns(self, model):
		_mc = ''
		for key in model._columns.keys():
			if model._columns[key]._db_type:
				_mc += ',' + self._get_column_name(model, key) + self._get_column_type(model, key) + self._get_column_size(model, key) + self._get_column_constraints(model, key)
		return _mc

	def _get_table_constraints(self, model):
		_sc = ''
		for c in model._sql_constraints:
			if c != model._rec_name:
				_sc += ',' + ' CONSTRAINT '+ c[0] + ' ' + c[1]
		return _sc

	def _get_schema_name(self, model):
		if model._sql_schema is None or model._sql_schema == 'public':
			return ''
		else:
			return model._sql_schema + '.'

	def _get_sql_schema_name(self, model):
		if model._sql_schema is None or model._sql_schema == 'public':
			return ''
		else:
			return model._sql_schema + '.'

	def _get_table_name(self, model):
		return model._get_table_name()

	def _get_sql_table_name(self, model):
		return self._get_schema_name(model) + model._table


	def _get_rec_name(self, model):
		if hasattr(model,'_recname'):
			return model._rec_name
		else:
			return None


	def _get_columns_attrs(self, model, columns = [], attrs = []):
		_res = {}
		if columns:
			lc = columns
		else:
			lc = self._columns.keys()

		for c in lc:
			_res[c] = self._columns[key]._get_attrs(c, attrs = attrs)

		return _res

	def _sql_create_sequence(self, model):
		_sql = []
		_sql.append("CREATE SEQUENCE " + self._get_table_name(model) + "_seq INCREMENT 1 MINVALUE 1 MAXVALUE " + str(2**63-1) + " START 1 CACHE 1 CYCLE")
		return _sql

	def _sql_create_index_of_table(self, model):
		_sql = []
		if model._log_access:
			_sql.append('CREATE INDEX ON '+ self._get_sql_table_name(model) + ' (create_uid)')
			_sql.append('CREATE INDEX ON '+ self._get_sql_table_name(model) + ' (write_uid)')

		for c in model._columns.keys():
			if (hasattr(model._columns[c],'select') and model._columns[c].select or model._columns[c]._type in ('many2one','related','state')) and  c != model._rec_name:
				_sql.append('CREATE INDEX ON '+ self._get_sql_table_name(model) + ' (' + c +')' )
		return _sql

	def _sql_create_table(self, model):
		_sql = []
		if len(model._columns) > 0:
			_sql.append("CREATE TABLE " + self._get_sql_table_name(model) + " (id integer primary key" + self._log_access_columns(model) + self._model_table_columns(model) + self._get_table_constraints(model) + ")")
		return _sql

	def _sql_create_table_comment(self, model):
		_sql = []
		_sql.append("COMMENT ON TABLE " + self._get_sql_table_name(model) + " IS " + "'" + model._description + "'")
		return _sql

	def _sql_create_columns_comment(self, model):
		_sql = []
		for key in model._columns.keys():
			if model._columns[key]._db_type:
				if model._columns[key].manual:
					_sql.append("COMMENT ON COLUMN " +self._get_table_name(model) +"." + key + " IS " + "'" + model._columns[key].manual + "'")
				else:
					_sql.append("COMMENT ON COLUMN " +self._get_table_name(model) +"." + key + " IS " + "'" + model._columns[key].label + "'")
		return _sql

	def _sql_alter_table(self,model):
		_sql = []
		_res.append(_sql)
		return _sql

	def _sql_drop_table(self,model):
		_sql = []
		_sql.append("drop table " + self._get_table_name())
		return _sql

	def alterModel(self, model, inherit, mode = 'add'):
		_sqls = []
		_sqls += self._sql_alter_table(model)
		self._execute(_sqls)
		_logger.info("Alter model %s" % (model.name,))

	def dropModel(self, model):
		_sqls = []
		_sqls += self._sql_drop_table(model)
		self._execute(_sqls)
		_logger.info("Drop model %s" % (model.name,))

	def createModel(self, model):
		if model._transient:
			return
		_sqls = []
		_sqls += self._sql_create_sequence(model)
		_sqls += self._sql_create_table(model)
		_sqls += self._sql_create_index_of_table(model)
		_sqls += self._sql_create_table_comment(model)
		_sqls += self._sql_create_columns_comment(model)
		self._dispatcher.db.pgdb._executeList(_sqls)
		_logger.info("Create model %s" % (model._name,))



# Build models - End


pgdbmodelManager()

