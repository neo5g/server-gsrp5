# -*- coding: utf-8 -*-

from functools import reduce
from collections import OrderedDict
from orm import fields
from orm.model import TransientModel

class ddl_model_database(TransientModel):
	_name = 'ddl.model.database'
	_description = 'Database Role'
	_columns = OrderedDict([
	('rolname', fields.varchar(label = 'Rolname',size=64)),
	('comment', fields.text(label = 'Comment'))
	])

ddl_model_database()
