# --*-- coding: utf-8 --*--

class MetaManager(type):

	__list_managers__ = {}


	def __new__(cls, name, bases, attrs):
		return super(MetaManager, cls).__new__(cls, name, bases, attrs)
		
	def __init__(self, name, bases, attrs):
		if not hasattr(self, '_register'):
			setattr(self,'_register',True)
		else:
			self._register = True

		super(MetaManager, self).__init__(name, bases, attrs)
		if hasattr(self,'_alias') and getattr(self,'_alias'):
			key = self._alias
			if hasattr(self,'_inherit') and self._inherit:
				key = self._inherit + '.' + self._alias
			MetaManager.__list_managers__[key] = self

class Manager(object, metaclass = MetaManager):
	_dispatcher = None
	_dispatch = None
	_name = None
	_alias = None
	_inherit = None

	def __new__(cls):
		return None
	
	@classmethod
	def create_instance(cls, dispatcher):
		obj = object.__new__(cls)
		obj._dispatcher = dispatcher
		obj._dispatch = dispatcher._dispatch
		obj.__init__()
		return obj




