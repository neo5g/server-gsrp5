#!/usr/bin/python3

from cli.SocketClient import NetRPCTCPV6Client as cli
msgs = []
msgs.append([['db.pgdb.login'],{'dsn':None,'database':'postgres' ,'user':'postgres','password':'admin','host':'localhost','port':5432}])
msgs.append([['db.pgdb.ddl.createRole'],{'rolname':'aa111a1b','password':'q1', 'comment':'Comment of role '}])
msgs.append([['db.pgdb.ddl.getRoleAttrs'],{'rolname':'aa111a1b'}])
msgs.append([['db.pgdb.ddl.dropRole'],{'rolname':'aa111a1b'}])
#msgs.append(['db.pgdb.ddl.createDatabase'],{'owner':'postgres', 'name':'a102','comment':'Coment of test', 'encoding':'UTF-8'}])
msgs.append([['db.pgdb.logout']])
s = cli(('localhost',8170))
for msg in msgs:
	print('MSG:',msg)
	rc = s.handle(msg)
	if rc:
		print('RC:',rc)
	else:
		print('RC:',rc)
s.client_close()
