# --*-- coding: utf-8 --*--

from flask import render_template, redirect
from managers.manager import Manager

class dbviewManager(Manager):
	"""
	Views для манипуляции базы данных
	"""
	_name = 'dbviewManager'
	_alias = 'view'
	_inherit = 'app.db'
	_list_methods = ('dbm',)

	def dbm(self):
		return render_template('dbm.html')

dbviewManager()
