# --*-- coding: utf-8 --*--

class MetaAPI(type):

	__list_modules__ = {}

	def __new__(cls, name, bases, attrs):
		obj = super(MetaAPI, cls).__new__(cls, name, bases, attrs)
		if obj.__module__ not in ('orm.api','orm.model','model'):
			MetaAPI.__list_modules__.setdefault(obj.__module__.split('.')[1],[]).append(obj)	
		return obj

	def __init__(self, name, bases, attrs):
		if not hasattr(self, '_register'):
		    setattr(self,'_register',True)
		else:
			self._register = True
		super(MetaAPI, self).__init__(name, bases, attrs)


class api(object, metaclass = MetaAPI):

	def create(self, vals):
		return self._dba._modelCreate(self,vals) 

	def search(self, where):
		return self._dba._modelSearch(self,where) 

	def read(self, ids, fields):
		return self._dba._modelRead(self, ids, fields) 

	def write(self, vals):
		return self._dba._modelWrite(self,vals) 

	def unlink(self, ids):
		return self._dba._modelUnlink(self,ids) 




if __name__ == "__main__":
	a= api()
	sql = a.create(None,1, {'c':2,'a':'Hello'})
	print('Sql =', sql)
