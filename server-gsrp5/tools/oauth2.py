import uuid


class OAuth2Method(object):
	def check(self,obj,attr):
		return True



class OAuth2(object):
	
	def __init__(self):
		pass

	def __getitem__(self,name):
		return self.__dict__[name]

	def __setitem__(self,name,value):
		self.__dict__[name] = value

	def RegisterUUID(self):
		u = uuid.uuid5(uuid.NAMESPACE_DNS,'gsrp.org')
		self.__dict__[u] = {}
		return u

	def unRegisterUUID(self,key):
		if key in self.__dict__:
			del self.__dict__[key]


if __name__ == "__main__":
	o= OAuth2()
	u=o.RegisterUUID()
	o[u] = {'Hello':'World'}
	print(o[u],u)
	import uuid
	
	hostnames = ['www.doughellmann.com', 'blog.doughellmann.com']
	
	for name in hostnames:
	    print(name)
	    print('\tMD5   :', uuid.uuid3(uuid.NAMESPACE_DNS, name))
	    print('\tSHA-1 :', uuid.uuid5(uuid.NAMESPACE_DNS, name))

