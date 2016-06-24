# --*-- coding: utf-8 --*--

from os.path import join as opj
import os
from lxml import etree
from managers.manager import Manager

class viewmodelManager(Manager):
	"""
	Загрузка view
	"""
	_name = 'viewmodelManager'
	_alias = 'model'
	_allow = {}
	_inherit = 'app.view'
	_list_methods = ('load', 'save')

	def load(self, name):
		fn = self._getFullFileName(name)
		if self._isGenerated:
			src = self._loadResoutceFromFile(fn+'.xml')
			html = self._generateFromXML(src)
		return jsonify({'json':render_template(name + '.html')})


	def loadCSS(self, name):
		return jsonify({'json':render_template(name + '.css')})

	def _getFullFileName(self, name):
		return opj(current_app.root_path, current_app.template_folder, name)

	def _isGenerated(self, name):
		if os.path.exists(name+'.html') and os.path.isfile(name+'.html') and os.path.getmtime(name+'.xml') > os.path.getmtime(name+'.html'):
			return True
		else:
			return False

	def _loadResoutceFromFile(self,fullname):
		f = open(fullname,'r')
		d = f.read()
		f.close()
		return d

	def _generateFromXML(self, data):
		tree = etree.fromstring(text = data)
		nodes = tree.xpath('/gsrp/data/template/form')
		for node in nodes:
			print(node.tag,node.keys(),node.values())
			for child in node.getchildren():
				print(child.tag,child.keys(),child.values())






	def save(self, name, value):
		pass

viewmodelManager()
