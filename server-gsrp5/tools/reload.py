# -*- coding: utf-8 -*-

import sys
import os
import logging
import threading
import time
import test

_logger = logging.getLogger('listener' + __name__)

class Reloader(object):
	_modules = {}
	def __init__(self, interval = 1.0):
		self.interval = interval
		list_modules = filter(lambda x: x[:2] != '' and '(built_in)' not in sys.modules[x],dir())
		for key in list_modules:
			module = sys.modules[key]
			filename = module.__file__
			timestamp = os.path.getmtime(filename)
			self._modules[key] = [module,filename,timestamp]
	def reload(self):
		for key in self._modules.keys():
			if os.path.getmtime(self._modules[key][1]) > self._modules[key][2]:
				reload(self._modules[key][0])
				print('Reloading module %s' %(self._modules[key][0].__name__,))
				_logger.info('Reloading module %s' % (self._modules[key][0].__name__,))

reloader = Reloader()

def change():
	time.sleep(reloader.interval)
	reloader.reload()

if __name__ == '__main__':
	t = threading.Thread(target=reloader, name='reloader')
	t.start()
