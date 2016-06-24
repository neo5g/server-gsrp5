# -*- coding: utf-8 -*-

import base64
import decimal
from psycopg2 import Binary
import datetime as DT
import pytz
import logging

_logger = logging.getLogger(__name__)

def _set_symbol(symb):
    if symb is None or symb == False:
        return None
    return str(symb)

class _column(object):

	__slots__ = ('__dict__','label', 'readonly', 'priority', 'domain', 'context', 'required', 'size', 'on_delete', 'on_update', 'change_default', 'translate', 'selections', 'selectable','filtering','manual', 'help', 'unique','selectable','timezone','obj','rel','id1','id2','offset','limit','check')

	def __init__(self, **kwargs):

		if len(kwargs) == 0:
			raise AttributesImpl

		for key in kwargs.keys():
			if key in self.__slots__ and key != "__dict__":
				setattr(self,key,kwargs[key])
			else:
				self.__dict__[key] = kwargs[key]


	def __contains__(self, name):
		if name != "__dict__" and name in self.__slots__:
			return True
		else:
			if name == "__dict__":
				return True
			else:
				return False

	def _get_symbol_c(self):
		if hasattr(self, '_symbol_c'):
			return self._symbol_set[0]
		else:
			raise AttributesImpl

	def _get_symbol_f(self, value):
		if hasattr(self, '_symbol_f'):
			return self._symbol_set[1](value)
		else:
			raise AttributesImpl

	def _get_attrs(self, attrs = []):
		result = {}

		if len(attrs) == 0:
			la = list(self.__slots__[1:]) + self.__dict__.keys()
		else:
			la = attrs

		for a in la:
			if self.__dict__.has_key(a):
				result[a] = self.__dict__[a]
			else:
				if hasattr(self,a):
					result[a] = getattr(self,a)

		return result


class char(_column):
	_classic_read =True
	_classic_write = True
	_prefetch = True
	_type = 'char'
	_db_type = 'character'
	_symbol_c = "%s"
	_symbol_f = _set_symbol
	_symbol_set = (_symbol_c, _symbol_f)
	_symbol_get = None

	def __init__(self, label = 'unknown', readonly = False, priority = 0, context = {}, required = False, size = 32, change_default = True, translate = False, selectable = False, filtering = None, domain=None, manual = False, help = False, unique = False, check = None):
		super(char, self).__init__(label=label, readonly=readonly, priority=priority, context=context, required = required, size = size, change_default = change_default, translate = translate, selectable = selectable, filtering=filtering, domain=domain, manual = manual, help=help, unique = unique, check = check)


class varchar(_column):
	_classic_read =True
	_classic_write = True
	_prefetch = True
	_type = 'varchar'
	_db_type = 'character varying'
	_symbol_c = "%s"
	_symbol_f = _set_symbol
	_symbol_set = (_symbol_c, _symbol_f)
	_symbol_get = None

	def __init__(self, label = 'unknown', readonly = False, priority = 0, context = {}, required = False, size = None, change_default = True, translate = False, selectable = False , filtering = None, domain=None, manual = False, help = False, unique = None, check = None):
		super(varchar, self).__init__(label=label, readonly=readonly, priority=priority, context=context, required = required, size = size, change_default = change_default, translate = translate, selectable = selectable, filtering = filtering, domain=domain, manual = manual, help=help, unique = unique, check = check)

class text(_column):
	_classic_read =True
	_classic_write = True
	_prefetch = False
	_type = 'text'
	_db_type = 'text'
	_symbol_c = "%s"
	_symbol_f = _set_symbol
	_symbol_set = (_symbol_c, _symbol_f)
	_symbol_get = None

	def __init__(self, label = 'unknown', readonly = False, priority = 0, context = {}, required = False, change_default = True, translate = False, manual = False, help = False):
		super(text,self).__init__(label = label, readonly = readonly, priority = priority, context = context, required = required, change_default = change_default, translate = translate, manual = manual, help = help)


class xml(_column):
	_classic_read =True
	_classic_write = True
	_prefetch = False
	_type = 'xml'
	_db_type = 'xml'
	_symbol_c = "%s"
	_symbol_f = _set_symbol
	_symbol_set = (_symbol_c, _symbol_f)
	_symbol_get = None

	def __init__(self, label = 'unknown', readonly = False, priority = 0, context = {}, required = False, change_default = True, translate = False, manual = False, help = False):
		super(xml,self).__init__(label = label, readonly = readonly, priority = priority, context = context, required = required, change_default = change_default, translate = translate, manual = manual, help= help)

class boolean(_column):
	_classic_read =True
	_classic_write = True
	_prefetch = True
	_type = 'boolean'
	_db_type = 'boolean'
	_symbol_c = "%s"
	_symbol_f = lambda x: x and 'True' or 'False'
	_symbol_set = (_symbol_c, _symbol_f)
	_symbol_get = None

	def __init__(self, label = 'unknown', readonly = False, priority = 0, context = {}, change_default = True, manual = False, help = False, selectable = None):
		super(boolean,self).__init__(label = label, readonly = readonly, priority = priority, context = context, change_default = change_default, manual = manual, help = help, selectable=selectable)

class integer(_column):
	_classic_read =True
	_classic_write = True
	_prefetch = True
	_type = 'integer'
	_db_type = 'integer'
	_symbol_c = "%s"
	_symbol_f = lambda x: int(x or 0)
	_symbol_set = (_symbol_c, _symbol_f)
	_symbol_get = lambda self, x: x or 0

	def __init__(self, label = 'unknown', readonly = False, priority = 0, context = {}, required = False, change_default = True, manual = False, help = False, check = None):
		super(integer,self).__init__(label = label, readonly = readonly, priority = priority, context = context, required = required, change_default= change_default, manual = manual, help = help, check = check)

class double(_column):
	_classic_read =True
	_classic_write = True
	_prefetch = True
	_type = 'double'
	_db_type = 'double precision'
	_symbol_c = "%s"
	_symbol_f = lambda x: float(x) or 0.0
	_symbol_set = (_symbol_c, _symbol_f)
	_symbol_get = lambda self, x: x or 0.0

	def __init__(self, label = 'unknown', readonly = False, priority = 0, context = {}, required = False, size = (15,3), change_default = True, manual = False, help = False, check = None):
		super(double,self).__init__(label = label, readonly = readonly, priority = priority, context = context, required = required, size = size, change_default = change_default, manual = manual, help = help, check = check)

class decimal(_column):
	_classic_read =True
	_classic_write = True
	_prefetch = True
	_type = 'decimal'
	_db_type = 'decimal'
	_symbol_c = "%s"
	_symbol_f = lambda x: decimal.Decimal(x) or decimal.Decimal('0.0')
	_symbol_set = (_symbol_c, _symbol_f)
	_symbol_get = lambda self, x: decimal.Decimal(x) or decimal.Decimal('0.0')

	def __init__(self, label = 'unknown', readonly = False, priority = 0, context = {}, required = False, size = (15,3), change_default = True, manual = False, help = False, check = None):
		super(decimal,self).__init__(label = label, readonly = readonly, priority = priority, context = context, required = required, size = size, change_default = change_default, manual = manual, help = help, check = check)

class numeric(_column):
	_classic_read =True
	_classic_write = True
	_prefetch = True
	_type = 'numeric'
	_db_type = 'numeric'
	_symbol_c = "%s"
	_symbol_f = lambda x: decimal.Decimal(x) or decimal/Decimal('0.0')
	_symbol_set = (_symbol_c, _symbol_f)
	_symbol_get = lambda self, x: decimal.Decimal(x) or decimal/Decimal('0.0')

	def __init__(self, label = 'unknown', readonly = False, priority = 0, context = {}, required = False, size = (15,3), change_default = True, manual = False, help = False):
		super(numeric,self).__init__(label = label, readonly = readonly, priority = priority, context = context, required = required, size =size, change_default = change_default, manual = manual, help = help)

class selection(_column):
	_classic_read =True
	_classic_write = True
	_prefetch = True
	_type = 'selection'
	_db_type = 'character varying'
	_symbol_c = "%s"
	_symbol_f = _set_symbol
	_symbol_set = (_symbol_c, _symbol_f)
	_symbol_get = None

	def __init__(self, label = 'unknown', selections = [],readonly = False, priority = 0, context = {}, required = False, size = 32, change_default = True, translate = False, selectable = False, manual = False, help = False, unique = None):
		super(selection,self).__init__(label = label, selections = selections,readonly = readonly, priority = priority, context = context, size = size, change_default = change_default, translate = translate, selectable = selectable, manual = manual, help = help, unique = unique)

class binary(_column):
	_classic_read =False
	_classic_write = False
	_prefetch = False
	_type = 'binary'
	_db_type = 'bytea'
	_symbol_c = "%s"
	_symbol_f = lambda symb: symb and Binary(str(symb)) or None
	_symbol_set = (_symbol_c, _symbol_f)
	_symbol_get = lambda self, x: x and str(x)

	def __init__(self, label = 'unknown', readonly = False, priority = 0, context = {}, required = False, change_default = True, manual = False, help = False):
		super(binary,self).__init__(label = label, readonly = readonly, priority = priority, context = context, required = required, change_default = change_default, manual = manual, help = help)

class date(_column):
	_classic_read =True
	_classic_write = True
	_prefetch = False
	_type = 'date'
	_db_type = 'date'
	_symbol_c = "%s"
	_symbol_f = lambda symb: symb or None
	_symbol_set = (_symbol_c, _symbol_f)
	_symbol_get = lambda self, x: x and str(x)

	def __init__(self, label = 'unknown', readonly = False, priority = 0, context = {}, required = False, change_default = True, manual = False, help = False):
		super(date,self).__init__(label = label, readonly = readonly, priority = priority, context = context, required = required, change_default = change_default, manual = manual, help = help)

	def today(self):
		return DT.datetime.today().strftime(tools.DEFAULT_SERVER_DATE_FORMAT)

	def context_today(self, timestamp = None, context = None):
		assert isinstance(timestamp, DT.datetime), 'Datetime instance expected'

		today = timestamp or DT.datetime.now()
		context_today = None

		if context and context.get('tz'):
			tz_name = context['tz']
		if tz_name:
			try:
				utc = pytz.timezone('UTC')
				context_tz = pytz.timezone(tz_name)
				utc_today = utc.localize(today, is_dst=False) # UTC = no DS
				context_today = utc_today.astimezone(context_tz)
			except Exception:
				_logger.debug("failed to compute context/client-specific today date, "
                              "using the UTC value for `today`",
                              exc_info=True)
		return (context_today or today).strftime(tools.DEFAULT_SERVER_DATE_FORMAT)


class datetime(_column):
	_classic_read =True
	_classic_write = True
	_prefetch = False
	_type = 'datetime'
	_symbol_c = "%s"
	_symbol_f = None
	_symbol_set = (_symbol_c, _symbol_f)
	_symbol_get = None

	def __init__(self, label = 'unknown', readonly = False, timezone = True, priority = 0, context = {}, required = False, change_default = True, manual = False, help = False):
		if timezone:
			self._db_type = 'timestamp with time zone'
		else:
			self._db_type = 'timestamp without time zone'
		super(datetime,self).__init__(label = label, readonly = readonly, timezone = timezone, priority = priority, context = context, required = required, change_default = change_default, manual = manual, help = help)

	def now(self):
		return DT.datetime.now().strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)

	def context_timestamp(self, timestamp, context):
		assert isinstance(timestamp, DT.datetime), 'Datetime instance expected'
		if context and context.get('tz'):
			tz_name = context['tz']
		if tz_name:
			try:
				utc = pytz.timezone('UTC')
				context_tz = pytz.timezone(tz_name)
				utc_timestamp = utc.localize(timestamp, is_dst=False) # UTC = no DS
				return utc_timestamp.astimezone(context_tz)
			except Exception:
				_logger.debug("failed to compute context/client-specific timestamp, "
                              "using the UTC value",
                              exc_info=True)
		return timestamp


class time(_column):
	_classic_read =True
	_classic_write = True
	_prefetch = False
	_type = 'time'
	_symbol_c = "%s"
	_symbol_f = lambda symb: symb and Binary(str(symb)) or None
	_symbol_set = (_symbol_c, _symbol_f)
	_symbol_get = lambda self, x: x and str(x)

	def __init__(self, label = 'unknown', readonly = False, timezone = True, priority = 0, context = {}, required = False, change_default = True, manual = False, help = False):
		if timezone:
			self._db_type = 'time with time zone'
		else:
			self._db_type = 'time without time zone'
		super(time,self).__init__(label = label, readonly = readonly, timezone = timezone, context = context, required = required, change_default = change_default, manual = manual, help = help)

	def time(self):
		return DT.datetime.now().strftime(tools.DEFAULT_SERVER_TIME_FORMAT)

	def context_time(self, timestamp = None, context = None):
		assert isinstance(timestamp, DT.datetime), 'Datetime instance expected'

		today = timestamp or DT.datetime.now()
		context_today = None

		if context and context.get('tz'):
			tz_name = context['tz']
		if tz_name:
			try:
				utc = pytz.timezone('UTC')
				context_tz = pytz.timezone(tz_name)
				utc_today = utc.localize(today, is_dst=False) # UTC = no DS
				context_today = utc_today.astimezone(context_tz)
			except Exception:
				_logger.debug("failed to compute context/client-specific today date, "
                              "using the UTC value for `today`",
                              exc_info=True)
		return (context_today or today).strftime(tools.DEFAULT_SERVER_TIME_FORMAT)


class function(_column):
	_classic_read =False
	_classic_write = False
	_prefetch = False
	_type = 'function'
	_db_type = None
	_symbol_c = "%s"
	_symbol_f = lambda symb: symb and Binary(str(symb)) or None
	_symbol_set = (_symbol_c, _symbol_f)
	_symbol_get = lambda self, x: x and str(x)

	def __init__(self, label = 'unknown', funcinv = None, funcinv_args = None, funcoutv = None, funcoutv_args = None, storage = False, method = True, type_result = float, readonly = False, priority = 0, context = {}, required = False, change_default = True, translate = False, manual = False, help = False):
		self._symbol_set[1] = funcinv
		self._symbol_get = funcoutv
		super(function,self).__init__(label = label, funcinv_args = funcinv_args, funcoutv_args = funcoutv_args, storage = storage, method = method,type_result = type_result, readonly = readonly, priority = prioryty, context = context, required = required, change_default = change_default, translate = translate, manual = manual, help = help)


class one2many(_column):
	_classic_read = False
	_classic_write = False
	_prefetch = False
	_type = 'one2many'
	_db_type = None
	def __init__(self, label='unknown', obj = None, rel = None, context = {}, offset = None, limit=None, manual = None, help = None):
		super(one2many,self).__init__(label = label, obj = obj, rel = rel, context = context, offset = offset,limit = limit, manual = manual,help = help)

class many2one(_column):
	_classic_read = False
	_classic_write = True
	_type = 'many2one'
	_db_type = 'integer'
	_symbol_c = '%s'
	_symbol_f = lambda x: x or None
	_symbol_set = (_symbol_c, _symbol_f)
	def __init__(self,label='unknown', obj = None, domain = None, context = {}, required = False, on_delete = None,manual = None, help = None):
		super(many2one,self).__init__(label = label, obj = obj, domain = domain, context = context, required = required, on_delete = on_delete, manual = manual, help = help)

class many2many(_column):
	"""Encapsulates the logic of a many-to-many bidirectional relationship, handling the
       low-level details of the intermediary relationship table transparently.
       A many-to-many relationship is always symmetrical, and can be declared and accessed
       from either endpoint model.
       If ``rel`` (relationship table name), ``id1`` (source foreign key column name)
       or id2 (destination foreign key column name) are not specified, the system will
       provide default values. This will by default only allow one single symmetrical
       many-to-many relationship between the source and destination model.
       For multiple many-to-many relationship between the same models and for
       relationships where source and destination models are the same, ``rel``, ``id1``
       and ``id2`` should be specified explicitly.

       :param str obj: destination model
       :param str rel: optional name of the intermediary relationship table. If not specified,
                       a canonical name will be derived based on the alphabetically-ordered
                       model names of the source and destination (in the form: ``amodel_bmodel_rel``).
                       Automatic naming is not possible when the source and destination are
                       the same, for obvious ambiguity reasons.
       :param str id1: optional name for the column holding the foreign key to the current
                       model in the relationship table. If not specified, a canonical name
                       will be derived based on the model name (in the form: `src_model_id`).
       :param str id2: optional name for the column holding the foreign key to the destination
                       model in the relationship table. If not specified, a canonical name
                       will be derived based on the model name (in the form: `dest_model_id`)
       :param str string: field label
	"""
	_classic_read = False
	_classic_write = False
	_prefetch = False
	_type = 'many2many'
	_db_type = None
	def __init__(self, label='unknown', obj = None, rel = None, id1 = None, id2 = None, offset = None,limit=None):
		super(many2many,self).__init__(label = label, obj = obj, rel = rel, id1 = id1, id2 = id2, offset = offset,limit = limit)

class related(_column):
	_classic_read = False
	_classic_write = True
	_type = 'relation'
	_db_type = 'integer'
	_symbol_c = '%s'
	_symbol_f = lambda x: x or None
	_symbol_set = (_symbol_c, _symbol_f)
	def __init__(self,label='unknown', obj = None, rel = None, context = {}, manual = None, help = None):
		super(related,self).__init__(label = label, obj = obj, rel = rel, context = context, manual = manual, help = help)

class state(_column):
	_classic_read = False
	_classic_write = True
	_type = 'state'
	_db_type = 'integer'
	_symbol_c = '%s'
	_symbol_f = lambda x: x or None
	_symbol_set = (_symbol_c, _symbol_f)
	def __init__(self,label='unknown', obj = None, rel = None, context = {}, manual = None, help = None):
		super(state,self).__init__(label = label, obj = obj, rel = rel, context = context, manual = manual, help = help)
