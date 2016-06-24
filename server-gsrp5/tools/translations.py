# --*-- coding: utf-8 --*--
import gettext
import locale

gettext.bindtextdomain('messages','./i18n')
gettext.bind_textdomain_codeset('messages',codeset = locale.getdefaultlocale()[1])
gettext.textdomain('messages')

def trlocal(message):
	return gettext.gettext(message)
