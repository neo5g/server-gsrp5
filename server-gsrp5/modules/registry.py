# --*-- coding: utf-8 --*--

from modules.loading import *
from orm import api 

class infoModule(dict):

	_name = None
	_module = None
	_info = {}
	_list_models = []
	_path = None
	_loaded = None

	def __init__(self, name, info, path):
		self._name = name
		self._info = info
		self._path = path
		self._module = None
		self._list_models = []
		self._models = {}
		self._loaded = None

	def _str__(self):
		return "name: %s\nmodule: %s\nModels: %s\n" % (self._name, self._module, self._models.keys())

	def _repr__(self):
		return "name: %s\nmodule: %s\nModels: %s\n" % (self._name, self._module, self._models.keys())


class Registry(object):

	_list_module_path = {}
	_list_modules = []
	_dict_models = {'basic':None,'addons':None}
	_dict_meta = None
	_pwd = None

	def __init__(self, dispatcher,root_path,list_module_path = {'basic':None,'addons':None}):
		self._dispatcher = dispatcher
		#self._pwd = os.getcwd()
		self._pwd = root_path
		self._list_module_path = list_module_path
		add_module_paths(root_path, self._list_module_path)
		self._load_modules_info()
		self._load_ddltools_modules()
		self._load_system_modules()
		self._load_preload_modules()

	def _load_module_info(self,path):
		return eval(load_resource_from_file(path,'__info__.py','rb'))

	def _load_modules_info(self):
		for d in list(self._list_module_path.keys()):
			mdir = opj(self._pwd,d)
			self._list_module_path[d] = list(filter(lambda x: os.path.isdir(opj(mdir,x)), os.listdir(mdir)))
		for path in list(self._list_module_path.keys()):
			for name in self._list_module_path[path]:
				if os.path.isdir(opj(self._pwd, path, name)) and os.path.exists(opj(self._pwd, path, name, '__info__.py')) and os.path.isfile(opj(self._pwd, path, name, '__info__.py')):
					self._list_modules.append(infoModule(name ,self._load_module_info(opj(self._pwd, path, name)), opj(self._pwd,path)))
		self._list_modules.sort(key = lambda x: len(x._info['depends']))

	def _load_ddltools_modules(self):
		listddltoolsload = list(filter(lambda x: 'system' in x._info and x._info['system'] == 'ddltools', self._list_modules))
		if len(listddltoolsload) == 0:
			return
		for module in listddltoolsload:
			module._module = load_module(module._path.split('/')[-1]+'.'+module._name)
			module._loaded = True
			if module._name == 'ddl':
				self._dict_meta = api.MetaAPI.__list_modules__
		for module in listddltoolsload:
			for model in self._dict_meta[module._name]:
				module._models[model._name] = model.create_instance()
				module._models[model._name]._db = self._dispatcher.db.pgdb
				module._models[model._name]._dbm = self._dispatcher.db.pgdb.model
				module._models[model._name]._dba = self._dispatcher.db.pgdb.api
				self._dispatcher.app.model._set(model._name, module._models[model._name])
				module._list_models.append(module._models[model._name])


	def _load_system_modules(self):
		listsystemload = list(filter(lambda x: 'system' in x._info and x._info['system'] == 'kernel', self._list_modules))
		if len(listsystemload) == 0:
			return
		for module in listsystemload:
			module._module = load_module(module._path.split('/')[-1]+'.'+module._name)
			module._loaded = True
			if module._name == 'bc':
				self._dict_meta = api.MetaAPI.__list_modules__
		for module in listsystemload:
			for model in self._dict_meta[module._name]:
				module._models[model._name] = model.create_instance()
				module._models[model._name]._db = self._dispatcher.db.pgdb
				module._models[model._name]._dbm = self._dispatcher.db.pgdb.model
				module._models[model._name]._dba = self._dispatcher.db.pgdb.api
				self._dispatcher.app.model._set(model._name, module._models[model._name])
				module._list_models.append(module._models[model._name])

	def _load_preload_modules(self):
		listPreload = list(filter(lambda x: 'preload' in x._info and x._info['preload'], self._list_modules))
		if len(listPreload) == 0:
			return
		for module in listPreload:
			module._module = load_module(module._path.split('/')[-1]+'.'+module._name)
			module._loaded = True
		for module in listPreload:
			for model in self._dict_meta[module._name]:
				module._models[model._name] = model.create_instance()
				module._models[model._name]._db = self._dispatcher.db.pgdb
				module._models[model._name]._dbm = self._dispatcher.db.pgdb.model
				module._models[model._name]._dba = self._dispatcher.db.pgdb.api
				self._dispatcher.app.model._set(model._name, module._models[model._name])
				module._list_models.append(module._models[model._name])

	def _load_others_modules(self):
		listotherload = list(filter(lambda x: not (('system' in x._info and x._info['system']) and not ( 'preload' in x._info and x._info['preload']) ), self._list_modules))
		if len(listotherload) == 0:
			return
		for module in listotherload:
			module._module = load_module(module._path.split('/')[-1]+'.'+module._name)
			module._loaded = True
		for module in listotherload:
			for model in self._dict_meta[module._name]:
				module._models[model._name] = model.create_instance()
				module._models[model._name]._db = self._dispatcher.db.pgdb
				module._models[model._name]._dbm = self._dispatcher.db.pgdb.model
				module._models[model._name]._dba = self._dispatcher.db.pgdb.api
				self._dispatcher.app.model._set(model._name, module._models[model._name])
				module._list_models.append(module._models[model._name])

	def _load_all_modules(self):
		if len(self._list_modules) == 0:
			return
		for module in self._list_modules:
			module._module = load_module(module._path.split('/')[-1]+'.'+module._name)
			module._loaded = True
		for module in self._list_modules:
			for model in self._dict_meta[module._name]:
				module._models[model._name] = model.create_instance()
				module._models[model._name]._dbm = self._dispatcher.db.pgdb.model
				self._dispatcher.app.model._set(model._name, module._models[model._name])
				module._list_models.append(module._models[model._name])
