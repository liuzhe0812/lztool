# -*- coding: utf-8 -*-
import MySQLdb
from module import globals
__author__ = 'liu'

class newDB:
    def __init__(self):
        self.host = None
        self.username = None
        self.password = None
        self.port = 3306
        self.charset = 'utf8'
        self.debug = None

    def connect(self):
        self.conn = MySQLdb.connect(self.host,self.username,self.password,port=int(self.port),charset=self.charset)
        self.cur = self.conn.cursor()

    def get_databases(self):
        db_list = []
        self.cur.execute('show databases')
        for db in self.cur.fetchall():
            db_list.append(db[0])
        return db_list

    def get_tables(self,dbname):
        "获取 所有表"
        table_list = []
        self.conn.select_db(dbname)
        self.cur.execute('show tables')
        for tb in self.cur.fetchall():
            table_list.append(tb[0])
        return table_list

    def get_table_info(self, tablename):
        "获取 表结构"
        self.cur.execute("DESC %s" % tablename)
        return self.cur.fetchall()

    def get_table_value(self, tablename):
        "获取 表内容"
        self.cur.execute("select * from %s" % tablename)
        result = self.cur.fetchall()
        return result

    def delete_item(self, tblname, dic):
        cols = ""
        for col in dic.keys():
            if dic[col] == None:
                continue
            if type(dic[col]) == int:
                tmp = "%s = %s" % (col, dic[col])
            else:
                tmp = "%s = '%s'" % (col, dic[col])
            if cols == "":
                cols = tmp
            else:
                cols = "%s and %s" % (cols, tmp)

        statement = "DELETE FROM %s WHERE %s" % (tblname, cols)
        cur = self.conn.cursor()
        print(statement)
        cur.execute(statement)
        cur.close()
        self.conn.commit()
        self.debug = u"执行：%s"%statement

    def add_item(self, tblname, dic):
        tableinfo = self.get_table_info(tblname)
        name_type = {}
        for item in tableinfo:
            name_type[item[0]] = item[1]
        cols = ""
        vals = ""
        for col in dic.keys():
            if cols == "":
                cols = col
            else:
                cols = "%s,%s" % (cols, col)
            if name_type[col].startswith('int'):
                val = dic[col]
            else:
                val = "'%s'" % dic[col]
            if vals == "":
                vals = val
            else:
                vals = "%s,%s" % (vals, val)
        statement = u"INSERT INTO %s (%s) VALUES (%s)" % (tblname,cols,vals)
        cur = self.conn.cursor()
        cur.execute(statement)
        cur.close()
        self.conn.commit()
        self.debug = u'执行：%s'%statement

    def update_item(self, tblname, dic, setdic):
        cols = ""
        for col in dic.keys():
            if dic[col] == None or not dic[col]:
                continue
            if type(dic[col]) == int:
                tmp = "%s = %s" % (col, dic[col])
            else:
                tmp = "%s = '%s'" % (col, dic[col])
            if cols == "":
                cols = tmp
            else:
                cols = "%s and %s" % (cols, tmp)

        setcols = ""
        for col in setdic.keys():
            tmp = "%s = '%s'" % (col, setdic[col])
            if setcols == "":
                setcols = tmp
            else:
                setcols = "%s ,%s" % (setcols, tmp)

        statement = "UPDATE %s SET %s WHERE %s" % (tblname, setcols, cols)
        cur = self.conn.cursor()
        cur.execute(statement)
        cur.close()
        self.conn.commit()
        self.debug = u'执行：%s'%statement

    def add_table(self, newtable, cols):
        fields = ""
        for item in cols.items():
            if len(fields) > 0:
                fields = "%s,%s %s" % (fields, item[0], item[1])
            else:
                fields = "%s %s" % (item[0], item[1])
        statment = "CREATE TABLE %s (%s)" % (newtable, fields)
        self.cur.execute(statment)
        self.conn.commit()
        self.debug = u'执行：%s'%statment

    def delete_table(self, tblname):
        statment = "DROP TABLE %s" % tblname
        self.cur.execute(statment)
        self.conn.commit()
        self.debug = u'执行：%s'%statment

    def cmd(self,cmd):
        self.cur.execute(cmd)
        return  self.cur.fetchall()

    def close(self):
        self.cur.close()
        self.conn.close()

class vdi_db:
    def __init__(self):
        self.conn = -1
        self.cur = -1
        self.host = -1

    def connect(self):
        self.conn = MySQLdb.connect(host=self.host, user='oseasy', passwd=globals.vdi_mysql_pwd, port=3306,
                                    charset="utf8")
        self.cur = self.conn.cursor()

    def get_inst_info(self, inst_id):
        data = self.cmd("select a.display_name,b.ip from nova.instances as a inner join auxo.nodes as b on a.host=b.name where a.uuid='%s' and b.deleted=0" % inst_id)
        name, host = data[0]

        data = self.cmd(
            "select volume_id,image_id from nova.block_device_mapping where instance_uuid='%s' and deleted=0 ORDER BY boot_index ASC" % inst_id)
        disk0 = data[0][0]
        disk0_image = data[0][1]
        disk1 = ''
        if len(data) == 1:
            disk1 = 'Null'
            disk1_image = 'Null'
        if len(data) >1 :
            disk1 = data[1][0]
            disk1_image = data[1][1]

        return (name, inst_id, host, disk0, disk1, disk0_image, disk1_image)

    def get_inst_UUID_from_userID(self,user_id):
        cmd = "select b.instance_id from thor_console.user_edu as a INNER JOIN thor_console.instance_extra as b where b.user_id=a.id and b.deleted=0 and b.graphic_type!='vnc' and a.id=%s" % user_id
        return self.cmd(cmd)

    def get_base_from_imageID(self,image_id):
        cmd = "select host,volume_id from cinder.image_volume_cache_entries where image_id='%s' order by id" % image_id
        return self.cmd(cmd)

    def disconnect(self):
        self.cur.close()
        self.conn.close()

    def cmd(self,cmd):
        self.cur.execute(cmd)
        return self.cur.fetchall()
