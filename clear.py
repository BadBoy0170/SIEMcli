#!/usr/bin/env python

   

import MySQLdb as mdb

con = mdb.connect('localhost', 'siemcli', 'siems2bfine',
        'siemclidb')
with con:
    cur = con.cursor()

    cur.execute('DROP TABLE IF EXISTS Entries')
