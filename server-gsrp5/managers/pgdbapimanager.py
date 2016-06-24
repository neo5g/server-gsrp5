# --*-- coding: utf-8 --*--

import logging
from managers.manager import Manager
from functools import reduce
from tools.translations import trlocal as _
_logger = logging.getLogger('listener.' + __name__)

class pgdbapi_exception(Exception): pass


class pgdbAPIManager(Manager):
	"""
	Обработка данных модели
	"""
	_name = 'pgdbAPIManager'
	_alias = 'api'
	_inherit = 'db.pgdb'

	def _getSQLSequence(self,name):
		self._db.cr.cr.callproc('nextval',[name])
		return self.cr.fetchone()[0]

# build master methods of model Read

	def _modelSearch(self, model, where, context = {}, limit = None, offset = None):
		_result = []
		_sqls = self._buildSQLSSearch(model,where,context,limit,offset)
		self._dispatcher.app.db._executeList(_sqls)
		for r in self._dispatcher.app.db.cr.fetchall():
			_result.append(r[0])
		return _result

	def _modelRead(self, model, ids, fields, context = {}, limit = None, offset = None):
		if type(ids) == int:
			_ids = tuple(ids)
		elif type(ids) in (tuple,list):
			_ids = ids
		if fields.__len__() == 0:
			_columns = filter(lambda x: hasattr(model,'_db_type') and model._db_type,model._columns.keys())
			_fetchmode = 'dict'
		else:
			_columns = fields
			_fetchmode = 'list'

		_sqls = self._buildSQLSRead(model=model, ids = _ids, fields = _columns, context = context, limit = limit, offset = offset) 
		_result = []
		for _sql in _sqls:
			self._dispatcher.app.db._executeList(_sqls)
			if _fetchmode == 'list':
				_result.extend(self._dispatcher.app.db.cr.fetchall())
			elif _fetchmode == 'dict':
				_result.extend(self._dispatcher.app.db.cr.fetchall())
		return _result

	def _modelCreate(self,model, vals, context = {}):
		if type(vals) == dict:
			_id,_sqls = self._buildSQLSCreate(model, vals, context)
			self._db._execute(_sqls)
			return _id 
		elif type(vals) in (tuple,list):
			_ids = []
			for val in vals:
				_id,_sqls = self._buildSQLSCreate(model,val,context)
				self._dispatcher.app.db._executeList(_sqls)
				_ids.append(_id)
			return _ids

	def _modelWrite(self, model, vals, context = {}):
		if type(vals) == dict:
			_id,_sqls = self._buildSQLSWrite(model,vals,context)
			self._db._execute(_sqls)
			return _id 
		elif type(vals) in (tuple,list):
			_ids = []
			for val in vals:
				_id,_sqls = self._buildSQLSWrite(model,val,context)
				self._dispatcher.app.db._executeList(_sqls)
				_ids.append(_id)
			return _ids

	def _modelUnlink(self, model, ids, context = {}):
		if type(ids) == int:
			_ids = tuple(ids)
		elif type(ids) in (tuple,list):
			_ids = ids
		_sqls = self._buildSQLSUnlink(model,_ids,context)
		self._dispatcher.app.db._executeList(_sqls)
		return True

# build sqls master methods of model Search	

	def _buildSQLSSearch(self, model, where, context, limit, offset):
		_sqls = []
		model_keys = model._columns.keys()
		model_db_fields = dict(filter(lambda x: getattr(x[1],'_db_type', False) or '_db_type' in x[1].__dict__ and x[1].__dict__['_db_type'],model._columns.items())).keys()
		for key,cond,val in where:
			if key.strip() not in model_db_fields:
				raise pgdb_exception(_('Database fields %s of model %s not avaliable') % (key, model._name))

		_where = ''
		_values_symbol_f = []
		for key,cond,val in where:
			if _where.__len__() == 0:
				_where += key.strip() + ' ' + cond.strip() + ' ' + model._columns[key]._symbol_set[0]
			else:
				_where += ' AND ' + key.strip() + ' ' + cond.strip()+ ' ' + model._columns[key]._symbol_set[0]
			if callable(model._columns[key]._symbol_set[1]):
				_values_symbol_f.append(model._columns[key]._symbol_set[1](val))
			else:
				_values_symbol_f.append(model._columns[key]._symbol_set[1])
		
		_sqls.append(self._dispatcher.app.db._mogrify("SELECT id FROM " + model._get_table_name() + " WHERE " + _where, _values_symbol_f))
		return _sqls

# build sqls master methods of model Read	

	def _buildSQLSRead(self,model, ids, fields, context, limit, offset):
		_sqls = []
		model_keys = model._columns.keys()
		model_db_fields = dict(filter(lambda x: getattr(x[1],'_db_type', False) or '_db_type' in x[1].__dict__ and x[1].__dict__['_db_type'],model._columns.items())).keys()
		model_one2many_fields = dict(filter(lambda x: hasattr(x[1],'_type') and getattr(x[1], '_type', False) == 'one2many' or '_type' in x[1].__dict__ and x[1].__dict__['_type'] == 'one2many',model._columns.items())).keys()
		
		for key in fields:
			if key not in model_keys:
				raise pgdb_exception(_('Fields %s of model %s not avaliable') % (key, model._name))

		if hasattr(model, '_order') and model._order == 'id':
			ids.sort()
		_count = int(ids.__len__() / 1000)
		_countlast = int(ids.__len__() % 1000)
		for i in range(_count):
			_sql = self._dispatcher.app.db._mogrify("SELECT id," + reduce(lambda x,y: x + ',' + y,fields) + " FROM " + model._get_table_name() + ' WHERE id IN (' + reduce(lambda x,y: x + ',' + y, ['%s'] * 1000) +')', ids[i * 1000: (i + 1) * 1000])
			_sqls.append(_sql)
		
		if _countlast > 0:
			_sql = self._dispatcher.app.db._mogrify("SELECT id," + reduce(lambda x,y: x + ',' + y,fields) + " FROM " + model._get_table_name() + ' WHERE id IN (' + reduce(lambda x,y: x + ',' + y, ['%s'] * _countlast) +')', ids[_count * 1000:]) 
			_sqls.append(_sql)
		return _sqls


# build sqls master methods of model Create

	def _buildSQLSCreate(self,model, vals, context):
		_sqls = []
		model_keys = model._columns.keys()
		model_required_keys = dict(filter(lambda x: getattr(x[1],'required', False) or 'required' in x[1].__dict__ and x[1].__dict__['required'],model._columns.items())).keys()
		model_db_fields = dict(filter(lambda x: getattr(x[1],'_db_type', False) or '_db_type' in x[1].__dict__ and  'one2many' in x[1].__dict__['_db_type'],model._columns.items())).keys()
		model_one2many_fields = dict(filter(lambda x: hasattr(x[1],'_type') and getattr(x[1], '_type', False) == 'one2many' or '_type' in x[1].__dict__ and x[1].__dict__['_type'] == 'one2many',model._columns.items())).keys()
		vals_keys = list(vals.keys())

		for key in vals_keys:
			if key not in model_keys:
				raise pgdb_exception(_('Fields %s of model %s not avaliable') % (key, model._name))

		for key in  model_required_keys:
			if key not in vals_keys:
				raise pgdb_exception(_('Fields %s of model %s is required. Field not present') % (key, model._name))
		_values_symbol_c = []
		_values_symbol_f = []
		for key in vals_keys:
			_values_symbol_c.append(model._columns[key]._symbol_set[0])
			if callable(model._columns[key]._symbol_set[1]):
				_values_symbol_f.append(model._columns[key]._symbol_set[1](vals[key]))
			else:
				_values_symbol_f.append(model._columns[key]._symbol_set[1])

		vals_keys.append('id')
		_id = model._getSQLSequence()
		_values_symbol_c.append('%s')
		_values_symbol_f.append(_id)
		if hasattr(model,'_log_access') and model._log_access:
			vals_keys.extend(['create_uid','create_datetime'])
			_values_symbol_c.extend(['%s','%s'])
			_values_symbol_f.extend([1,datetime.utcnow()])
		_fields = reduce(lambda x,y: x + ','  + y, vals_keys)
		_sql = self._dispatcher.app.db._mogrify("INSERT INTO " + model._get_table_name() + "(" + _fields +") VALUES(" + reduce(lambda x,y: x + ',' + y,_values_symbol_c) + ")",_values_symbol_f)
		print('MOGRIFY',type(_sql),_sql)
		_sqls.append(_sql)
		return _id, _sqls

# build sqls master methods of model Write

	def _buildSQLSWrite(self,model, vals, context):
		_sqls = []
		model_keys = model._columns.keys()
		model_required_keys = dict(filter(lambda x: getattr(x[1],'required', False) or 'required' in x[1].__dict__ and x[1].__dict__['required'],model._columns.items())).keys()
		model_db_fields = dict(filter(lambda x: getattr(x[1],'_db_type', False) or '_db_type' in x[1].__dict__ and x[1].__dict__['_db_type'],model._columns.items())).keys()
		model_one2many_fields = dict(filter(lambda x: hasattr(x[1],'_type') and getattr(x[1], '_type', False) == 'one2many' or '_type' in x[1].__dict__ and x[1].__dict__['_type'] == 'one2many',model._columns.items())).keys()
		vals_keys = list(filter(lambda x: x != 'id',vals.keys()))

		for key in vals_keys:
			if key not in model_keys:
				raise pgdb_exception(_('Fields %s of model %s not avaliable') % (key, model._name))
				
			if key in model_required_keys and vals[key] is None:
				raise pgdb_exception(_('Fields %s of model %s is required. Value not present') % (key, model._name))

			if key in ('write_uid','write_datetime'):
				raise pgdb_exception(_('Fields %s of model %s is invalid name') % (key, model._name))

		_values_symbol_c = []
		_values_symbol_f = []
		for key in vals_keys:
			_values_symbol_c.append(model._columns[key]._symbol_set[0])
			if callable(model._columns[key]._symbol_set[1]):
				_values_symbol_f.append(model._columns[key]._symbol_set[1](vals[key]))
			else:
				_values_symbol_f.append(model._columns[key]._symbol_set[1])

		if model._log_access:
			vals_keys.append('writete_uid')
			vals_key.append('write_datetime')
			_values_symbol_c.extend(['%s','%s'])
			_values_symbol_f.extend([1,datetime.utcnow()])


		_set = ''
		for i in range(vals_keys.__len__()):
			key  = vals_keys[i]
			_c = _values_symbol_c[i]
			if _set.__len__() == 0:
				_set += key + ' = ' + _c
			else:
				_set += ',' + key + ' = ' + _c
		_where =  'WHERE id = %s' % (vals['id'],)
		_sql = self._dispatcher.app.db._mogrify("UPDATE " + model._get_table_name() + " SET " + _set + _where, _values_symbol_f)
		_sqls.append(_sql)
		return vals['id'],_sqls

# build sqls master methods of model Unlink

	def _buildSQLSUnlink(self,model, ids, context):
		_sqls = []
		model_one2many_fields = dict(filter(lambda x: hasattr(x[1],'_type') and getattr(x[1], '_type', False) == 'one2many' or '_type' in x[1].__dict__ and x[1].__dict__['_type'] == 'one2many',model._columns.items())).keys()
	
		_count = int(ids.__len__() / 1000)
		_countlast = int(ids.__len__() % 1000)
		for i in range(_count):
			_sql = self._dispatcher.app.db._mogrify("DELETE FROM " + model._get_table_name() + ' WHERE id IN (' + reduce(lambda x,y: x + ',' + y, ['%s'] * 1000) +')', ids[i * 1000: (i + 1) * 1000])
			_sqls.append(_sql)
		
		if _countlast > 0:
			_sql = self._dispatcher.app.db._mogrify("DELETE FROM " + model._get_table_name() + ' WHERE id IN (' + reduce(lambda x,y: x + ',' + y, ['%s'] * _countlast) +')', ids[_count * 1000:]) 
			_sqls.append(_sql)
		return _sqls

pgdbAPIManager()
