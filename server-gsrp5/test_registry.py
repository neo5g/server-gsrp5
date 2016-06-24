#!/usr/bin/python3

import os
import managers
from dispatcher.dispatcher import Dispatcher
dispatcher = Dispatcher(managers.manager.MetaManager.__list_managers__, os.getcwd())
dispatcher.app.db.login(database='tst',user='aaa12345',password='12345678')
dispatcher.app.db._execute('drop schema if exists tst cascade')
dispatcher.app.db._execute('create schema tst')
res = dispatcher.app.module._install_system_modules()
dispatcher.app.db.commit()
dispatcher.app.db.logout()
