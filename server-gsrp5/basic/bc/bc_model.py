# -*- coding, utf-8 -*-

from collections import OrderedDict
from orm import fields
from orm.model import Model

class bc_users(Model):
    _name = 'bc.users'
    _description = 'Users'
    _log_access = False
    _rec_name = 'login'
    _columns = OrderedDict([
	('login_id', fields.integer(label = 'Login Identification',check = "login_id > 0 and login_id <= 100")),
	('login', fields.varchar('Login', required = True, size = 32)),
	('pswd', fields.varchar('Pqssword', required = True, size = 32)),
	('firstname', fields.varchar('First Name', required = True, selectable = True)),
	('lastname', fields.varchar('Last Name', required = True, selectable = True))
	])
    _sql_constraints = [('full_name_unique','unique (firstname, lastname)', 'Login unique fullname of user')]

bc_users()

class bc_group_module(Model):
	_name = 'bc.group.module'
	_description = 'General Module Group'
	_table = 'bc_group_module'
	_columns = OrderedDict([
	('name', fields.varchar(label = 'Name')),
	('name2', fields.varchar(label = 'Name 2', selectable = True, required = True)),
	('parent_id', fields.integer(label = 'Parent')),
	('bc_module', fields.one2many(label = 'Basic module',obj = 'bc.module', rel = 'bc_group_module_id')),
	('note', fields.text('Note'))
	])

bc_group_module()

class bc_module(Model):
	_name = 'bc.module'
	_description = 'General module'
	_table = 'bc_module'
	_columns = OrderedDict([
	('bc_group_module_id',fields.many2one(label = 'Model Group', obj = 'bc.group.module', required = True, on_delete = 'n')),
	('name', fields.varchar(label = 'Name')),
	('version', fields.varchar(label = 'Version')),
	('category', fields.varchar(label = 'Name')),
	('short_description', fields.varchar(label = 'Short Description', size = 256)),
	('long_description', fields.text(label = 'Long Description')),
	('author', fields.varchar(label = 'Author', size =128 )),
	('website', fields.varchar(label = 'Website', size =128 )),
	('maintainer', fields.varchar(label = 'Maintainer', size = 128)),
	('installable', fields.boolean(label = 'Installable')),
	('auto_install', fields.boolean(label = 'Auto Install')),
	('category', fields.selection(label = 'Category',selections = [('S','System'), ('A','Application'), ('E','Extra')])),
	('icon', fields.varchar(label = 'Icon', size = 64)),
	('image', fields.varchar(label = 'Image ', size = 64)),
	('models',fields.one2many(label ='Models', obj = 'bc.model', rel = 'module_id')),
	('state',fields.selection(label = 'State', selections = [('N','Not installed'),('I','Installed'),('i','To be installed'),('u','To be upgrade')]))
	])

bc_module()

class bc_model(Model):
	_name = 'bc.model'
	_description = 'General model'
	_table = 'bc_model'
	_columns = OrderedDict([
	('name',fields.varchar(label = 'Name', size = 64)),
	('dbtable', fields.varchar(label = 'Database table', size = 64)),
	('description', fields.varchar(label = 'Short Description', size = 256)),
	('module_id', fields.many2one(label = 'Module', obj = 'bc.module')),
	('columns',fields.one2many(label = 'Columns', obj = 'bc.model.columns', rel = 'model_id'))
	])

bc_model()

class bc_model_columns(Model):
	_name = 'bc.model.columns'
	_description = 'General model'
	_table = 'bc_model_columns'
	_columns = OrderedDict([
	('name',fields.varchar(label = 'Name', size = 64)),
	('model_id',fields.many2one(label = 'Model', obj = 'bc.model')),
	('label', fields.varchar(label = 'label', size = 64)),
	('readanly',fields.boolean(label = 'Readonly')),
	('priority',fields.integer(label = 'Prority')),
	('domain',fields.text(label = 'Domain')),
	('required',fields.boolean(label = 'Required')),
	('size', fields.integer(label = 'Size')),
	('precesion', fields.integer(label = 'Precesion')),
	('on_delete',fields.selection(label = 'On delete',selections = [('a','No action'),('r','Restrict'),('n','Set Null'),('c','Cascade'),('d','Set default')], size = 1)),
	('on_update',fields.selection(label = 'On delete',selections = [('a','No action'),('r','Restrict'),('n','Set Null'),('c','Cascade'),('d','Set default')], size = 1)),
	('change_default',fields.boolean(label = 'Change default')),
	('translate',fields.boolean(label = 'Translate')),
	('selectable', fields.boolean(label = 'Select')),
	('manual', fields.text(label = 'Manual')),
	('help', fields.text(label = 'Help')),
	('isunique',fields.boolean(label = 'Unique')),
	('selections', fields.text(label = 'Selection')),
	('timezone',fields.boolean(label = 'Timezone')),
	('obj',fields.varchar(label = 'Obj', size = 64)),
	('rel',fields.varchar(label = 'Relation', size = 64)),
	('id1',fields.varchar(label = 'Id1', size = 64)),
	('id2',fields.varchar(label = 'Id2', size = 64))
	])

class bc_model_data(Model):
	_name = 'bc.model.data'
	_description = 'Loading model xml data'
	_columns = OrderedDict([
	('name',fields.varchar(label = 'Name',size = 128)),
	('module',fields.varchar(label = 'Module',size = 64)),
	('model',fields.varchar(label = 'Model',size = 64)),
	('rec_id', fields.integer(label = 'ID record')),
	('date_init',fields.datetime(label = 'Timestamp init', timezone = False)),
	('date_update',fields.datetime(label = 'Timestamp update', timezone = False))
	])

class bc_ui_view(Model):
	_name = 'bc.ui.view'
	_description = 'General models views'
	_table = 'bc_ui_view'
	_columns = OrderedDict([
	('name',fields.varchar(label = 'Name', size = 64)),
	('model', fields.varchar(label = 'Model Name', size = 64)),
	('arch_fs', fields.text(label = 'Arch Filename')),
	('type', fields.selection(label = 'Arch Type', selections = [('xml','Xml'),('html','Html')])),
#	'view_type', fields.selection(label = 'View Type', selections = [('form','Form'),('list','List'),('tree','Tree'),('graph','Graph'),('calendar','Calendar'),('gantt','Gantt'),('mdx','MDX'),('kanban','Kanban')]),
	('arch',fields.xml(label = 'Arch Blob'))
	])

bc_ui_view()

class bc_ui_menu(Model):
	_name ='bc.ui.menu'
	_description = 'Application menu'
	_table = 'bc_ui_menu'
	_columns = OrderedDict([
	('name',fields.varchar(label = 'Name')),
	('parent_id',fields.integer(label='Parent ID')),
	('parent_left',fields.integer(label='Left Parent')),
	('parent_rigth',fields.integer(label='Rigth Parent')),
	('web_icon',fields.varchar(label='Web Icon', size=255))
	])

bc_ui_menu()
