# -*- coding: utf-8 -*-

from functools import reduce
from collections import OrderedDict
from orm import fields
from orm.model import TransientModel



class ddl_model_role(TransientModel):
	_name = 'ddl.model.role'
	_description = 'Database Role'
	_columns = OrderedDict([
	('rolname', fields.varchar(label = 'Rolname',size=64)),
	('comment', fields.text(label = 'Comment'))
	])

ddl_model_role()

