# --*-- coding: utf-8 --*--

import os
import sys
from os.path import join as opj
from lxml import etree
from io import StringIO, BytesIO
from managers.manager import Manager
from modules.loading import load_resource_from_file


class moduleManager(Manager):
	"""
	Обработка данных модуля
	"""
	_name = 'moduleManager'
	_alias = 'module'
	_inherit = 'app'

	_list_module_path = {'basic':None,'addons':None}
	_pwd = None

	def __init__(self):
		super(moduleManager,self).__init__()

	def _readXMLattribute(self, items, name):
		return filter(lambda x: x[0] == name, items)[0][1]

	def _loadXML(self,p,f):
		list_records =[]
		record = {}
		record_id = None
		model = None
		#xml = load_resource_from_file(p,f,'rb')
		#print('TYPE XML',type(xml))
		xml = open(opj(p,f,),'rb')
		root = etree.iterparse(xml,events = ['start','end'],tag = 'model',remove_blank_text = True,encoding = None)
		for event, element in root:
			if event == 'start':
				if element.tag == 'model':
					model = element.attrib['model']
					for child in element.iterchildren():
						if child.tag == 'column':
							name = child.attrib['name']
							if 'type' in child.attrib and child.attrib['type'] in ('StringField','PasswordField'):
								pass
							else:
								value = child.text
							record[name] = value
				else:
					continue
			elif event == 'end':
				if element.tag == 'record':
					list_records.append([record_id,model,record])
			else:
				continue
		xml.close()
		print(list_records)
		
	def _install_system_modules(self):
		sysmodules = list(filter(lambda x: 'system' in x._info and x._info['system'],self._dispatcher._registry._list_modules))
		sysmodules.sort(key = lambda x: len(x._info['depends']))		   
		for module in sysmodules:
			for model in module._list_models:
				self._dispatcher.app.db.model.createModel(model)
				if model._name == 'bc.users':
					_id = self._dispatcher.app.model.get(model._name).create([{'login_id':1,'login':'admin','pswd':'123iop','firstname':'Administrator','lastname':'GSRP'},{'login_id':2,'login':'admin1','pswd':'123iop1','firstname':'Administrator1','lastname':'GSRP1'},{'login_id':3,'login':'admin3','pswd':'123iop3','firstname':'Administrator3','lastname':'GSRP3'}])
					print('IDS ',_id)
					_ids_search = self._dispatcher.app.model.get(model._name).search([('login','=','admin')])
					print('IDS SEARCH',_ids_search)
					for ids in _ids_search:
						self._dispatcher.app.model.get(model._name).write([{'login':'admin2','id':ids}])
					_ids_search = self._dispatcher.app.model.get(model._name).search([('login','=','admin3')])
					_res = self._dispatcher.app.model.get(model._name).read(_ids_search,['login', 'login_id'])
					print('IDS SEARCH',_ids_search)
					print('READ',_res)
					self._dispatcher.app.model.get(model._name).unlink(_ids_search)
					self._dispatcher.app.db.commit()
			self._loadXML(opj(os.getcwd(),'basic/bc'),'bc_view.xml')

moduleManager()
