# -*- coding: utf-8 -*-
from collections import OrderedDict
from orm import fields
from orm.model import Model

class md_group_model(Model):
	_name = 'md.group.model'
	_description = 'General model Group'
	_table = 'md_group_model'
	_columns = OrderedDict([
	('name', fields.varchar(label = 'Name')),
	('parent_id', fields.integer('Parent')),
	('md_model', fields.one2many(obj = 'md.model',rel = 'md_group_model_id',label = 'Model')),
	('note', fields.text(label = 'Note'))
	])

md_group_model()

class md_model(Model):
	_name = 'md.model'
	_description = 'General model'
	_table = 'md_model'
	_columns = OrderedDict([
	('md_group_model_id', fields.many2one(obj = 'md.group.model',label = 'Model Group')),
	('name', fields.varchar(label = 'Name')),
	('note', fields.text(label = 'Note'))
	])

md_model()


