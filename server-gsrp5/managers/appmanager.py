    # --*-- coding: utf-8 --*--

from managers.manager import Manager
from managers.pgdbmanager import pgdbManager
class appManager(Manager):
	"""
	Обработка данных приложений на стороне сервера
	"""
	_name = 'appManager'
	_alias = 'app'

	def __call__(self, *args, **kwargs):
		if self._name[:3] == 'app' and self._name.find('.') > 0:
			keys = self._name.split('.')[1:]
			method = self
			for key in keys:
				method = getattr(method,key)
			return method.__call__(*args,**kwargs)
		else:
			method = getattr(method,self._name)
			return method.__call__(*args,**kwargs)


appManager()
