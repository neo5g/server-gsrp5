# -*- coding: utf-8 -*-

from collections import OrderedDict
from orm import fields
from orm.model import Model

class md_group_model1(Model):
	_name = 'md.group.model1'
	_description = 'General model Group'
	_table = 'md_group_model1'
	_columns = OrderedDict([
	('name', fields.varchar(label = 'Name')),
	('parent_id', fields.integer(label = 'Parent')),
	('md_model', fields.one2many(obj = 'md.model',rel = 'md_group_model_id',label = 'Model')),
	('note', fields.text('Note'))
	])

md_group_model1()

class md_model1(Model):
	_name = 'md.model1'
	_description = 'General model'
	_table = 'md_model1'
	_columns = OrderedDict([
	('md_group_model_id', fields.many2one(obj = 'md.group.model1',label = 'Model Group')),
	('name', fields.varchar(label = 'Name')),
	('note', fields.text(label = 'Note'))
	])

md_model1()


