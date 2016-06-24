# --*-- coding: utf-8 --*--

from managers.manager import Manager
from tools.translations import trlocal as _

class modelException(Exception): pass

class modelManager(Manager):
	"""
	Обработка данных модели
	"""
	_name = 'modelManager'
	_alias = 'model'
	_inherit = 'app'
	_models = {}

	def _set(self, name, model):
		if not name in  self._models:
			self._models[name] = model
		else:
			raise modelException(_("app.model:Model %s is exist" % (name,)))
		
	def get(self, name):
		if name in self._models:
			return self._models[name]
		else:
			raise modelException(_("app.model:Model %s is not exist" % (name,)))

	def apply(self, name, method, kwargs = None):
		#print('GETATTR:',getattr(self.get(name),method), dir(self.get(name)))
		if kwargs and kwargs.__len__() > 0:
			return getattr(self.get(name),method)(**kwargs)
		else:
			return getattr(self.get(name),method)()
	
	def count(self, model, **kwargs):
		return self.get(model).count(**kwargs)

	def search(self, model, **kwargs):
		return self.get(model).search(**kwargs)
	
	def read(self, model, **kwargs):
		return self.get(model).read(**kwargs)

	def write(self, model, **kwargs):
		return self.get(model).write(**kwargs)

	def create(self, model, **kwargs):
		return self.get(model).create(**kwargs)

	def unlink(self, model, **kwargs):
		return self.get(model).unlink(**kwargs)

	def ddlcreate(self, model, **kwargs):
		return self.get(model).ddlcreate(**kwargs)

	def alter(self, model, **kwargs):
		return self.get(model).alter(**kwargs)

	def drop(self, model, **kwargs):
		return self.get(model).drop(**kwargs)



modelManager()
