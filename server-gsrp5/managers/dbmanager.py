# --*-- coding: utf-8 --*--

from managers.manager import Manager

class dbManager(Manager):
	"""
	Root db access manager
	"""
	_name = 'dbManager'
	_alias = 'db'
	_switch = {}
	_dbmanager = 'pgdb'
	
	def __init__(self):
	    self._switch['db'] = {'pgdb':None,'oradb':None,'cocroachdb':None}
	    super(dbManager, self).__init__()

	def __getattr__(self, name):
		if name == 'db':
			return self._switch[name][self._dbmanager]


	def __call__(self, *args, **kwargs):
		if self._name[:2] == 'db' and self._name.find('.') > 0:
			keys = self._name.split('.')[1:]
			method = self
			for key in keys:
				method = getattr(method,key)
			return method.__call__(*args,**kwargs)
		else:
			method = getattr(method,self._name)
			return method.__call__(*args,**kwargs)
	
dbManager()
