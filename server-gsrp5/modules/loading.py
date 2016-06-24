# -*- coding: utf-8 -*-

import os
import sys
import importlib
from os.path import join as opj

def add_module_paths(root_path, list_module_path):
	map(lambda y: sys.path.append(opj(root_path,y)) ,filter(lambda x: os.path.isdir(opj(root_path,x)), os.listdir(root_path)))
	for key in list_module_path.keys():
	    list_module_path[key] = filter(lambda x: os.path.isdir(opj(x)), os.listdir(opj(root_path,key)))

def load_resource_from_file(path,name,mode = "rb"):
	if  os.path.exists(opj(path, name)) and os.path.isfile(opj(path, name)):
		try:
			with open(opj(path, name), mode) as f:
				d = f.read()
				f.close()
				return d
		finally:
			try:
				f.close()
			except:
				pass

	else:
		return None

def load_module(name, package = None):
	return importlib.import_module(name,package)

def load_module_info(path):
	i = load_resource_from_file(path,'__info__.py','rb')
	if i:
		return eval(i)
	else:
		return {}
