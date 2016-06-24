from distutils.core import setup, Extension

module1 = Extension('listener', sources = ['listener.c'])
                    
setup (name = 'listener', version = '1.0', description = 'Listener',ext_modules = [module1])

