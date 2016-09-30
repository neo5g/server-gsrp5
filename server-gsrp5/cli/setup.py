from distutils.core import setup, Extension

module1 = Extension('SocketClient', sources = ['SocketClient.c'])
module2 = Extension('addrinfo', sources = ['addrinfo.c'])
module3 = Extension('packer', sources = ['packer.c'])

                    
setup (name = 'SocketClient', version = '1.0', description = 'Sockets of client package',ext_modules = [module1,module2,module3])

import os
import sys
#os.execvp('cython',['-3','SocketClient.py','addrinfo.py','packer.py'])
ext =[]
lf = list(filter(lambda x: x[0] != '_' and x != 'setup.py' and x[-3:] == '.py' and os.path.isfile(x),os.listdir('./')))
print(lf)
for l in lf:
    ext.append(Extension(l[:-3],sources = [l[:-3]+'.c']))
module1 = Extension('SocketClient', sources = ['SocketClient.c'])
module2 = Extension('addrinfo', sources = ['addrinfo.c'])
module3 = Extension('packer', sources = ['packer.c'])
print(ext)
                    
setup (name = 'SocketClient', version = '1.0', description = 'Sockets of client package',ext_modules = ext)


