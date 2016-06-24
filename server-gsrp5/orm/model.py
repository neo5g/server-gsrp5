# --*-- coding: utf-8 --*--

import sys
import logging
from functools import reduce
from orm.common import *
from tools.translations import trlocal as _
from orm.api import api
from orm.fields import _column
from io import StringIO
from collections import OrderedDict

_logger = logging.getLogger(__name__)

class orm_exception(Exception):
	def __init__(self, *args, **kwargs):
		self.args = args
		self.kwargs = kwargs


class browse_null(object):

	def __init__(self):
		self.id = False

	def __getitem__(self,name):
		return None

	def __getattr__(self,name):
		return None

	def __int__(self):
		return False

	def __str__(self):
		return ''

	def __nonzero__(self):
		return False

	def __unicode__(self):
		return u''

class browse_record_list(list):
	def __init__(self, record, context = {}):
		super(browse_record_list, self).__init__(record)
		self.context = context

class browse_record(object):

	def __init__(self, vals, context = {}):
		super(browse_record, self).__init__()

		#self.cr = cr
		self.uid =vals['uid']
		self.id = vals['id']
		self.context = context

		for k in vals.keys():
			self.__dict__[k] = vals[k]

	def __str__(self,name):
		return unicode(str(self.__dict__[name]))

	def __repr__(self):
		return str(self)

	def __getattr__(self, name):
		return self.__dict__[name]

	def __setattr__(self, name, value):
		self.__dict__[name] = value

class BaseModel(api):
	_sql_schema = "tst"
	_name = None
	_table = None
	_description = None
	_trigers = {}
	_columns = OrderedDict()
	_default = {}
	_register = False
	_constraints = []
	_sql_constraints = []
	_rec_name = "name"
	_parent = "parent_id"
	_order_by = "id"
	_state = "state"
	_date_name = "date"
	_sequence = "sequence"
	_sql_sequence = None
	_active = "active"
	_auto = True

	@classmethod
	def create_instance(cls):
		""" Instanciate a given model.

        This class method instanciates the class of some model (i.e. a class
        deriving from osv or osv_memory). The class might be the class passed
        in argument or, if it inherits from another class, a class constructed
        by combining the two classes.

        The ``attributes`` argument specifies which parent class attributes
        have to be combined.

        TODO: the creation of the combined class is repeated at each call of
        this method. This is probably unnecessary.

		"""
		attributes = ['_columns', '_defaults', '_inherits', '_constraints','_sql_constraints', '_sql_schema']
		obj = object.__new__(cls)
		obj.__init__()
		return obj

	def __new__(cls):
		return None

	def __init__(self):

        #if not self._name and not hasattr(self, '_inherit'):
            #name = type(self).__name__.split('.')[0]
            #msg = "The class %s has to have a _name attribute" % name

            #_logger.error(msg)
            #raise except_orm('ValueError', msg)

		if hasattr(self, '_list_columns'):
			for name,field in self._list_columns:
				self._columns[name] = field
			self._list_columns.clear()			
		
		if not self._description:
			self._description = self._name
		if self._transient:
			self._table = None
		else:
			if not self._table:
				self._table = self._name.replace('.', '_')
		if self._table and self._table[:3].lower() == 'pg_':
			raise orm_exception([_('Invalid table name'), self._table, self._name])
		if self._transient:
			self._log_access = False
		else:
			if not hasattr(self, '_log_access'):
			## If _log_access is not specified, it is the same value as _auto.
				self._log_access = getattr(self, "_auto", True)

		if self._rec_name not in  self._columns.keys():
			self._rec_name = None
		if self._table:
			self._sql_sequence = self._get_table_name() + '_seq'
			
	def browse(self, ids, fields = None):
		if fields and fields.__len__() > 0:
			_columns = fields
		else:
			_columns = filter(lambda x:self._columns[x]._db_type, self._columns.keys())
		l = self.read(ids, _columns)
		if l.__len__() > 0:
			brl = browse_record_list()
			for r in l:
				br = browse_record()
				if type(r) == dict:
					for k in r.keys():
						setattr(br,k,r[k])
				elif type(r) in (tuple,list):
					for i in xrange(_columns.__len__()):
						setattr(br,_columns[i],r[i])
				brl.append(br)
			return brl
		else:
			return browse_null()

	def _get_schema_name(self):
		if self._transient:
			return None
		if self._sql_schema is None or self._sql_schema == 'public':
			return ''
		else:
			return self._sql_schema + '.'
			  
	def _get_table_name(self):
		if self._transient:
			return None
		return self._get_schema_name() + self._table
	
	def _getSQLSequence(self):
		self._db.cr.cr.callproc('nextval',[self._sql_sequence])
		return self._db.cr.fetchone()[0]

	def _buildXMLForDynamicModel(self):
		_mapped_attributes = {'_type':'type'}
		f = StringIO()
		f.write('<?xml version="1.0"?>')
		f.write('<model>')
		for key in self._columns.keys():
			s = '<column name="'+name+'"'
			f = self._columns[key]
			for k in ('_type','label'):
				if k in _mapped_attributes:
					key = _mapped_attributes[k]
				else:
					key = k
				s += ' '+key+'"'+self._columns[k]+'"'
			f.write(s+'/>')
		f.write('/<model>')
		f.seek(0)
		return f

# Общие методы построения SQL запроса

	def _count_clause(self):
		return "SELECT count(*)"

	def _search_clause(self):
		return "SELECT a.oid as id"

	def _offset_clause(self, offset):
		if offset: 
			if type(offset) == int:
				return " OFFSET %s" % (offset,)
			else:
				raise TypeError
		else:
			return ''

	def _limit_clause(self, limit):
		if limit: 
			if type(limit) == int:
				return " LIMIT %s" % (limit,)
			else:
				raise TypeError
		else:
			return ''

	def _select_clause(self):
		return "SELECT "

	def _fields_clause(self, fields):
		_f = OrderedDict([('id','a.oid AS id'),('nspname','a.nspname AS nspname'),('owner','b.rolname AS owner'),('comment','d.description AS comment')])
		if fields and fields.__len__() > 0:
			v = []
			if 'id' not in fields:
				v['id'] = _f['id']
			for f in fields:
				if f in _f:
					v.append(_f[f])
				else:
					raise AttributeError
		else:
			for key in _f.keys():
				v.append(_f[key])
		return reduce(lambda x,y: x+','+y,v)

	def _from_clause(self):
		return " FROM (pg_namespace AS a INNER JOIN pg_authid AS b ON(a.nspowner=b.oid) LEFT OUTER JOIN pg_description AS d ON(a.oid=d.objoid)) LEFT OUTER JOIN pg_class AS c ON (d.classoid = c.oid AND c.relname = 'pg_namespace')"

	def _where_clause(self,cond = None):
		res = ''
		if cond:
			res = reduce(lambda x,y: x+' AND '+y,map(lambda x: x[0]+' '+x[1]+' '+x[2], cond))
		filtering = self._filtering_clause()
		if filtering:
			if res.__len__() > 0:
				res+= ' AND ' + filtering
			else:
				res = filtering
		domain = self._domain_clause()
		#print('ddd',domain)
		if domain:
			if res.__len__() > 0:
				res+= ' AND ' + domain
			else:
				res = domain
		if res.__len__() > 0:
			res = ' WHERE' + res
		return res

	def _ids_clause(self, tids):
		if type(tids) == int:
			" WHERE a.oid=%s"
		elif type(tids) in (tuple,list,set):
			return " WHERE a.oid in (%s)"
			
	def _ids_where_clause(self,sql,ids):
		_sqls =[]
		if type(ids) == int:
			return list().append(sql+self._ids_clause() % (ids,))
		elif type(ids) in (tuple,list,set):
			if type(ids) == set:
				l = list(ids)
			else:
				l= ids
			for i in range(int(l.__len__()/1000)):
				_sql= sql+self._ids_clause() %  reduce(lambda x,y:x+','+y ,map(lambda x: str(x),l[:i*1000]))
				_sql+=self._order_by_clause()
				_sqls.append(_sql)
			_sql= sql+self._ids_clause(ids) %  reduce(lambda x,y:x+','+y ,map(lambda x: str(x),l[0-(l.__len__() % 1000):]))
			_sql+=self._order_by_clause()
			_sqls.append(_sql)

		else:
			raise TypeError
		return _sqls

	def _order_by_clause(self):
		if hasattr(self, '_order_by'):
			if type(self._order_by) in (str,bytes):
				return ' ORDER BY %s' % self._order_by
			elif type(self._order_by) in (tuple,list):
				return ' ORDER BY %s' % reduce(lambda x,: x+','+y, self._order_by)
		else:
			return ''

	def _group_by_clause(self):
		if hasattr(self, '_group_by'):
			if type(self._group_by) in (str,bytes):
				return ' GROUP BY %s' % self._group_by
			elif type(self._group_by) in (tuple,list):
				return ' GROUP BY %s' % reduce(lambda x,: x+','+y, self._group_by)
		else:
			return ''

	def _filtering_clause(self):
		res = ''
		for n,v in filter(lambda x: hasattr(x[1],'filtering') and x[1].filtering,self._columns.items()):
			#print('FILTERING:',n,v.filtering)
			for f in v.filtering:
				if f.__len__() == 1:
					pass
				elif f.__len__() == 2:
					if res.__len__() == 0:
						res+= ' '
					else:
						res+= ' AND '
					res+= n + ' ' + f[0] + " '" + f[1] + "'"
		if res.__len__() == 0:
			return None
		else:
			return res

	def _domain_clause(self):
		res = ''
		for n,v in filter(lambda x: hasattr(x[1],'domain') and x[1].domain,self._columns.items()):
			#print('DOMAIN:',n,v.domain)
			for f in v.domain:
				if f.__len__() == 1:
					pass
				elif f.__len__() == 2:
					pass
				elif f.__len__() == 3:
					if res.__len__() == 0:
						res+= ' '
					else:
						res+= ' AND '
					res+= f[0] + ' ' + f[1] + ' ' + " '" + f[2] + "'"
		if res.__len__() == 0:
			return None
		else:
			return res

	def modelInfo(self, columns = None, attributes = None):
		mi = {'header':{'model':self._name,'description':self._description,'recname':self._recname},'columns':self.columnsInfo(columns,attributes)}
		#print('MODEL INFO:',mi)
		return mi

	def columnsInfo(self, columns = None, attributes = None):
		res = {}
		if columns:
			cols = columns
		else:
			cols = list(self._columns.keys())
		
		if attributes:
			attrs = attributes
		else:
			attrs = list(filter(lambda x: x != '__dict__',_column.__slots__))
		if '_type' not in attrs:
			attrs.extend(['_type'])
		#print('COLS:',cols)
		#print('ATTRS:',attrs)	
		for column in cols:
			info = {}
			for attr in attrs:
				if column != 'id' and hasattr(self._columns[column],attr):
					info[attr] = getattr(self._columns[column],attr)
				if column != 'id' and hasattr(self._columns[column],'__dict__'):
					for key in self._columns[column].__dict__.keys():
						#print('KEY:',column,key)
						info[key] = self._columns[column].__dict__[key]
			if column != 'id':
				res[column] = info
			else:
				res[column] = {'required':True,'_type':'integer','label':'ID Record'}
		return res

	def count(self, cond = None, context = {}):
		self._db._execute(self._count_clause()+self._from_clause()+self._where_clause(cond))
		return self._db.cr.fetchone()[0]

	def search(self, cond = None, context = {}, limit = None, offset = None):
		#print('SQL:',self._search_clause()+self._from_clause()+self._where_clause(cond)+self._limit_clause(limit)+self._offset_clause(offset))
		self._db._execute(self._search_clause()+self._from_clause()+self._where_clause(cond)+self._order_by_clause()+self._limit_clause(limit)+self._offset_clause(offset))
		res = list(map(lambda x: x[0],self._db.cr.fetchall()))
		#print('Result:',res)
		return res
		
	
	def read(self, ids, fields = None, context = {}):
		_sqls = self._ids_where_clause(self._select_clause()+self._fields_clause(fields)+self._from_clause(),ids)
		result = []
		for _sql in _sqls:
			self._db._execute(_sql)
			result.extend(self._db.cr.fetchall())
		#print('Read result:',fields,result)
		return result


class Model(BaseModel):
	_transient = None

class TransientModel(BaseModel):
	_transient = True


