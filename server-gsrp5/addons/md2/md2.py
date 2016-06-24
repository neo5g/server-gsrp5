# -*- coding: utf-8 -*-

from orm import fields
from orm.model import Model

class md_group_model2(Model):
	_name = 'md.group.model2'
	_description = 'General model Group'
	_table = 'md_group_model2'
	_columns = OrderedDict([
	('name', fields.varchar(label = 'Name')),
	('parent_id', fields.integer(label = 'Parent')),
	('md_model', fields.one2many(obj = 'md.model',rel = 'md_group_model_id',label = 'Model')),
	('note', fields.text(label = 'Note'))
	])

md_group_model2()

class md_model2(Model):
	_name = 'md.model2'
	_description = 'General model'
	_table = 'md_model2'
	_columns = OrderedDict([
	('md_group_model_id', fields.many2one(obj = 'md.group.model',label = 'Model Group',manual = u"Это свзязь с группой иоделей")),
	('name', fields.varchar(label = 'Name')),
	('note', fields.text(label = 'Note'))
	])

md_model2()


