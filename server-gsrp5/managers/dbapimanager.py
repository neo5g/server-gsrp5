# --*-- coding: utf-8 --*--

import logging
from managers.dbmanager import dbManager
from tools.translations import trlocal as _
_logger = logging.getLogger('listener.' + __name__)

class dbapi_exception(Exception): pass


class pgdbAPIManager(dbManager):
	"""
	Обработка данных модели
	"""
	_name ='pgdbAPIManager'
	_alias = 'api'
	_inherit = 'db.pgdb'

	def _getSQLSequence(self,name):
		self.cr.cr.callproc('nextval',[name])
		return self.cr.fetchone()[0]

# build master methods of model Read

	def _modelSearch(self, model, where):
		_result = []
		_sqls = self._buildSQLSSearch(model,where)
		self._execute(_sqls)
		for r in self.cr.fetchall():
			_result.append(r[0])
		return _result

	def _modelRead(self, model, ids, fields):
		if type(ids) in (int,long):
			_ids = tuple(ids)
		elif type(ids) in (tuple,list):
			_ids = ids
		if fields.__len__() == 0:
			_columns = filter(lambda x: hasattr(model,'_db_type') and model._db_type,model._columns.keys())
			_fetchmode = 'dict'
		else:
			_columns = fields
			_fetchmode = 'list'

		_sqls = self._buildSQLSRead(model=model, ids = _ids, fields = _columns) 
		_result = []
		for _sql in _sqls:
			self._execute(_sql)
			if _fetchmode == 'list':
				_result.extend(self.cr.fetchall())
			elif _fetchmode == 'dict':
				_result.extend(self.cr.dictfetchall())
		return _result

	def _modelCreate(self,model, vals):
		if type(vals) == dict:
			_id,_sqls = self._buildSQLSCreate(model,vals)
			self._execute(_sqls)
			return _id 
		elif type(vals) in (tuple,list):
			_ids = []
			for val in vals:
				_id,_sqls = self._buildSQLSCreate(model,val)
				self._execute(_sqls)
				_ids.append(_id)
			return _ids

	def _modelWrite(self, model, vals):
		if type(vals) == dict:
			_id,_sqls = self._buildSQLSWrite(model,vals)
			self._execute(_sqls)
			return _id 
		elif type(vals) in (tuple,list):
			_ids = []
			for val in vals:
				_id,_sqls = self._buildSQLSWrite(model,val)
				self._execute(_sqls)
				_ids.append(_id)
			return _ids

	def _modelUnlink(self, model, ids):
		if type(ids) in (int,long):
			_ids = tuple(ids)
		elif type(ids) in (tuple,list):
			_ids = ids
		_sqls = self._buildSQLSUnlink(model,_ids)
		self.cr._execute(_sqls)
		return True

# build sqls master methods of model Search	

	def _buildSQLSSearch(self, model, where):
		_sqls = []
		model_keys = model._columns.keys()
		model_db_fields = dict(filter(lambda x: getattr(x[1],'_db_type', False) or x[1].__dict__.has_key('_db_type') and x[1].__dict__['_db_type'],model._columns.items())).keys()
		for key,cond,val in where:
			if key.strip() not in model_db_fields:
				raise pgdb_exception(_('Database fields %s of model %s not avaliable') % (key, model._name))

		_where = ''
		_values_symbol_f = []
		for key,cond,val in where:
			if _where.__len__() == 0:
				_where += key.strip() + ' ' + cond.strip() + ' ' + model._columns[key]._symbol_set[0]
			else:
				_where += ' AND ' + key.strip() + ' ' + cond.strip() + model._columns[key]._symbol_set[0]
			if callable(model._columns[key]._symbol_set[1]):
				_values_symbol_f.append(model._columns[key]._symbol_set[1](val))
			else:
				_values_symbol_f.append(model._columns[key]._symbol_set[1])
		
		_sqls.append(self._mogrify("SELECT id FROM " + self._get_table_name(model) + " WHERE " + _where, _values_symbol_f))
		return _sqls

# build sqls master methods of model Read	

	def _buildSQLSRead(self,model, ids, fields):
		_sqls = []
		model_keys = model._columns.keys()
		model_db_fields = dict(filter(lambda x: getattr(x[1],'_db_type', False) or x[1].__dict__.has_key('_db_type') and x[1].__dict__['_db_type'],model._columns.items())).keys()
		model_one2many_fields = dict(filter(lambda x: hasattr(x[1],'_type') and getattr(x[1], '_type', False) == 'one2many' or x[1].__dict__.has_key('one2many') and x[1].__dict__['_type'] == 'one2many',model._columns.items())).keys()
		
		for key in fields:
			if key not in model_keys:
				raise pgdb_exception(_('Fields %s of model %s not avaliable') % (key, model._name))

		if hasattr(model, '_order') and model._order == 'id':
			ids.sort()
		_count = ids.__len__() / 1000
		_countlast = ids.__len__() % 1000
		for i in xrange(_count):
			_sql = self._mogrify("SELECT id," + reduce(lambda x,y: x + ',' + y,fields) + " FROM " + self._get_table_name(model) + ' WHERE id IN (' + reduce(lambda x,y: x + ',' + y, ['%s'] * 1000) +')', ids[i * 1000: (i + 1) * 1000])
			_sqls.append(_sql)
		
		if _countlast > 0:
			_sql = self._mogrify("SELECT id," + reduce(lambda x,y: x + ',' + y,fields) + " FROM " + self._get_table_name(model) + ' WHERE id IN (' + reduce(lambda x,y: x + ',' + y, ['%s'] * _countlast) +')', ids[_count * 1000:]) 
			_sqls.append(_sql)
		return _sqls


# build sqls master methods of model Create

	def _buildSQLSCreate(self,model, vals):
		_sqls = []
		model_keys = model._columns.keys()
		model_required_keys = dict(filter(lambda x: getattr(x[1],'required', False) or x[1].__dict__.has_key('required') and x[1].__dict__['required'],model._columns.items())).keys()
		model_db_fields = dict(filter(lambda x: getattr(x[1],'_db_type', False) or x[1].__dict__.has_key('_db_type') and x[1].__dict__['_db_type'],model._columns.items())).keys()
		model_one2many_fields = dict(filter(lambda x: hasattr(x[1],'_type') and getattr(x[1], '_type', False) == 'one2many' or x[1].__dict__.has_key('one2many') and x[1].__dict__['_type'] == 'one2many',model._columns.items())).keys()
		vals_keys = vals.keys()

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
		_id = self._getSQLSequence(self._get_table_name(model) + '_seq')
		_values_symbol_c.append('%s')
		_values_symbol_f.append(_id)
		if hasattr(model,'_log_access') and model._log_access:
			vals_keys.extend(['create_uid','create_datetime'])
			_values_symbol_c.extend(['%s','%s'])
			_values_symbol_f.extend([1,datetime.utcnow()])
		_fields = reduce(lambda x,y: x + ','  + y, vals_keys)
		_sql = self._mogrify("INSERT INTO " + self._get_table_name(model) + "(" + _fields +") VALUES(" + reduce(lambda x,y: x + ',' + y,_values_symbol_c) + ")",_values_symbol_f)
		print('MOGRIFY',type(_sql,_sql))
		_sqls.append(_sql)
		return _id, _sqls

# build sqls master methods of model Write

	def _buildSQLSWrite(self,model, vals):
		_sqls = []
		model_keys = model._columns.keys()
		model_required_keys = dict(filter(lambda x: getattr(x[1],'required', False) or x[1].__dict__.has_key('required') and x[1].__dict__['required'],model._columns.items())).keys()
		model_db_fields = dict(filter(lambda x: getattr(x[1],'_db_type', False) or x[1].__dict__.has_key('_db_type') and x[1].__dict__['_db_type'],model._columns.items())).keys()
		model_one2many_fields = dict(filter(lambda x: hasattr(x[1],'_type') and getattr(x[1], '_type', False) == 'one2many' or x[1].__dict__.has_key('one2many') and x[1].__dict__['_type'] == 'one2many',model._columns.items())).keys()
		vals_keys = filter(lambda x: x != 'id',vals.keys())

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
		for i in xrange(vals_keys.__len__()):
			key  = vals_keys[i]
			_c = _values_symbol_c[i]
			if _set.__len__() == 0:
				_set += key + ' = ' + _c
			else:
				_set += ',' + key + ' = ' + _c
		_where =  'WHERE id = %s' % (vals['id'],)
		_sql = self._mogrify("UPDATE " + self._get_table_name(model) + " SET " + _set + _where, _values_symbol_f)
		_sqls.append(_sql)
		return vals['id'],_sqls

# build sqls master methods of model Unlink

	def _buildSQLSUnlink(self,model, ids):
		_sqls = []
		model_one2many_fields = dict(filter(lambda x: hasattr(x[1],'_type') and getattr(x[1], '_type', False) == 'one2many' or x[1].__dict__.has_key('one2many') and x[1].__dict__['_type'] == 'one2many',model._columns.items())).keys()
	
		_count = ids.__len__() / 1000
		_countlast = ids.__len__() % 1000
		for i in xrange(_count):
			_sql = self._mogrify("DELETE FROM " + self._get_table_name(model) + ' WHERE id IN (' + reduce(lambda x,y: x + ',' + y, ['%s'] * 1000) +')', ids[i * 1000: (i + 1) * 1000])
			_sqls.append(_sql)
		
		if _countlast > 0:
			_sql = self._mogrify("DELETE FROM " + self._get_table_name(model) + ' WHERE id IN (' + reduce(lambda x,y: x + ',' + y, ['%s'] * _countlast) +')', ids[_count * 1000:]) 
			_sqls.append(_sql)
		return _sqls

dbAPIManager()
