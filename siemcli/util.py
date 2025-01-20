#!/usr/bin/env python

   

# MariaDB connection module, for testing purposes
# Usage:
# import siemcli.util
# db = siemcli.util.SiemConnect()
# rows = db.x('select * from Auth')
# db.x('drop table if exists Auth')


import MySQLdb as mdb


class SiemConnect:

    def __init__(self, server='127.0.0.1', user='siemcli',
            password='siems2bfine', database='siemclidb'):
        self.server = server
        self.user = user
        self.password = password
        self.database = database
        self.con = None
        self.cur = None

        self.connect()


    def connect(self):
        self.con = mdb.connect(self.server, self.user, self.password,
                self.database)
        self.cur = con.cursor(mdb.cursors.DictCursor)

    def disconnect(self):
        self.cur.close()
        self.con.close()


    def x(self, statement):
        self.cur.execute(statement)
        if statement.startswith('SELECT') or statement.startswith('select'):
            return cur.fetchall
        else:
            return
