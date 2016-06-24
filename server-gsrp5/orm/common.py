# -*- coding: utf-8 -*-


LOG_ACCESS_COLUMNS = {
    'create_uid':'integer REFERENCES %sbc_users ON DELETE SET NULL',
    'create_datetime':'timestamp without time zone',
    'write_uid':'integer REFERENCES %sbc_users ON DELETE SET NULL',
    'write_datetime':'timestamp  without time zone'
    }

MAGIC_COLUMNS = ['id']
for k in LOG_ACCESS_COLUMNS.keys():
	MAGIC_COLUMNS.append(k)

MAP_TYPES_FIELDS_TO_DB = {'boolean':'boolean','char':'character','varchar':'character varying','integer':'integer' ,
'many2one': 'integer','text':'text','float':'real','double':'double precision','numeric':'numeric', 'decimal':'decimal', 
'binary':'bytea','selection':'character varying'}

FIELDS_TYPE_NO_DB = ('one2many','function','many2many')

RESTRCT_TYPE_DB = {'a':' NO ACTION','r':' RESTRICT','n':' SET NULL','c':' CASCADE','d':' SET DEFAULT'}

RESERVED_KYEWORD_POSTGRESQL = ['ALL', 'ANALYSE', 'ANALYZE', 'AND', 'ANY', 'ARRAY', 'AS', 'ASYMETRIC', 'BOTH', 'CASE', 'CAST','CHECK', 'COLUMN', 'CONCURENTLY',
'CONSTRAINT','CREATE','CROSS','CURRENT_CATALOG','CURRENT_DATE','CURRENT_ROLE','CURRENT_SCHEMA','CURRENT_TIME','CURRENT_TIMESTAMP','CURRENT_USER','DEFAULT', 
'DEFERABLE','DESC','DISTINCT','DO','ELSE','END','EXCEPT','FALSE','FETCH','FOR','FOREIGN','FREZZE','FROM','FULL','GRANT','GROUP','HAVING','ILIKE','IN','INOTIALLY',
'INTERSECT','INTO', 'IS','ISNULL','JOIN', 'LEADING','LEFT','LIMIT','LOCALTIME','LOCALTIMESTAMP','NATURAL','NOT','NOTNULL','NULL','OFFSET','ON','ONLY','OR','ORDER',
'OUTER','OVER','OVERLAPS','PLACING','PRIMARY','REFERENCES','RIGTH','SELECT','SESSION_USER','SIMULAR','SOME','SYMMETRIC','TABLE','THEN','TRAILING','TRUE','INION',
'UNIQUE','USER','USING','VERBOSE','WHEN','WHERE']

SQL_RESERVED_KEYWORDS = RESERVED_KYEWORD_POSTGRESQL

