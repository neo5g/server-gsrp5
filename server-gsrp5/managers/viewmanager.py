# --*-- coding: utf-8 --*--

from managers.manager import Manager

class viewManager(Manager):
	"""
	Загрузка View
	"""
	_name = 'viewManager'
	_alias = 'view'
	_inherit = 'app'

viewManager()
