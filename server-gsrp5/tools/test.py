# -*- coding: utf-8 -*-

import sys
import os
import logging
import threading
import time
import test

_logger = logging.getLogger('listener' + __name__)

class Test(object):
	_modules = {}
	def __init__(self):
		g = globals()
		print('G',g)
		list_modules = filter(lambda x: x[:2] != '__'  and sys.modules.has_key(x) and not ('(built_in)' in str(sys.modules[x])),g)
		for key in list_modules:
			if sys.modules.has_key(key):
				module = sys.modules[key]
				print('MODULE',module,dir(module))
				filename = module.__file__
				timestamp = os.path.getmtime(filename)
				self._modules[key] = [module,filename,timestamp]
	def reload(self):
		for key in self._modules.keys():
			if os.path.getmtime(self._modules[key][1]) > self._modules[key][2]:
				reload(self._modules[key][0])
				print('Reloading module %s' %(self._modules[key][0].__name__,))
				_logger.info('Reloading module %s' % (self._modules[key][0].__name__,))

test = Test()

