#!/usr/bin/env python

   

import logdissect.parsers
import time
from datetime import datetime
import re
import sys
import os
import MySQLdb as mdb


def simple_query(db, table='siem_default', last='24h', shost=None,
        process=None, grep=None):
    """Query siemcli SQL database for events (simplified)"""

    qstatement = []
    qstatement.append("SELECT * FROM " + table)
    
    if last[-1:] == 'm': timeint = 'minute'
    elif last[-1:] == 's': timeint = 'second'
    elif last[-1:] == 'd': timeint = 'day'
    else: timeint = 'hour'

    qstatement.append("WHERE date_stamp >= timestamp(date_sub(now(), " + \
            "interval " + str(int(last[:-1])) + " " + timeint + "))")
    
    if shost: qstatement.append("AND source_host LIKE \"" + shost + "\"")
    if process:
        qstatement.append("AND source_process LIKE \"" + process + "\"")
    if grep: qstatement.append("AND message LIKE \"%" + grep + "%\"")

    qstatement = " ".join(qstatement)
    con = mdb.connect(db['host'], db['user'], db['password'], db['database'])

    with con:
        cur = con.cursor()
        cur.execute(qstatement)

        rows = cur.fetchall()
        desc = cur.description
    cur.close()
    con.close()

    return desc, rows

def query(db, tables=[], columns=[],
        last=None, daterange=None, ids=[], sourcehosts=[],
        sourceports=[], desthosts=[], destports=[], processes=[],
        pids=[], protocols=[], greps = [],
        rsourcehosts=[], rsourceports=[], rdesthosts=[],
        rdestports=[], rprocesses=[], rpids=[], rprotocols=[],
        rgreps=[], rulequery=False):
    """Query siemcli SQL database for events"""
    
    lastunits = {'d': 'day', 'h': 'hour', 'm': 'minute', 's': 'second'}
    
    qstatement = []

    # Select statement (columns)
    if columns:
        statement = "SELECT " + columns[0]
        for column in columns[1:]:
            statement += ", " + column
    else:
        statement = "SELECT *"
    qstatement.append(statement)
    
    # From statement (tables)
    statement = "FROM " + tables[0]
    for table in tables[1:]:
        statement += ", " + table
    qstatement.append(statement)

    # Initial where statement (time period)
    if daterange:
        startdate, enddate = daterange.split('-')
        statement = "WHERE date_stamp BETWEEN \"" + startdate + \
                "\" AND \"" + enddate + "\""
    elif last:
        lastunit = lastunits[last[-1]]
        lastnum = last[:-1]

        statement = "WHERE date_stamp >= " + \
                "timestamp(date_sub(now(), interval " + \
                lastnum + " " + lastunit + "))"
    else:
        statement = "WHERE date_stamp >= " + \
                "timestamp(date_sub(now(), interval " + \
                "1 day))"
    qstatement.append(statement)


    # Include attributes
    if ids:
        statement = "AND (id LIKE \"" + \
                ids[0] + "\""
        for i in ids[1:]:
            statement += " OR id LIKE \"" + i + "\""
        statement += ")"
        qstatement.append(statement)

    if sourcehosts:
        statement = "AND (source_host LIKE \"" + \
                sourcehosts[0] + "\""
        for host in sourcehosts[1:]:
            statement += " OR source_host LIKE \"" + host + "\""
        statement += ")"
        qstatement.append(statement)

    if sourceports:
        statement = "AND (source_port LIKE \"" + \
                sourceports[0] + "\""
        for port in sourceports[1:]:
            statement += " OR source_port LIKE \"" + port + "\""
        statement += ")"
        qstatement.append(statement)

    if desthosts:
        statement = "AND (dest_host LIKE \"" + \
                desthosts[0] + "\""
        for host in desthosts[1:]:
            statement += " OR dest_host LIKE \"" + host + "\""
        statement += ")"
        qstatement.append(statement)

    if destports:
        statement = "AND (dest_port LIKE \"" + \
                destports[0] + "\""
        for port in destports[1:]:
            statement += " OR dest_port LIKE \"" + port + "\""
        statement += ")"
        qstatement.append(statement)

    if processes:
        statement = "AND (source_process LIKE \"" + \
                processes[0] + "\""
        for process in processes[1:]:
            statement += " OR source_process LIKE \"" + process + "\""
        statement += ")"
        qstatement.append(statement)
    
    if pids:
        statement = "AND (source_pid LIKE \"" + \
                pids[0] + "\""
        for pid in pids[1:]:
            statement += " OR source_pid LIKE \"" + pid + "\""
        statement += ")"
        qstatement.append(statement)
    
    if protocols:
        statement = "AND (protocol LIKE \"" + \
                protocols[0] + "\""
        for protocol in protocols[1:]:
            statement += " OR protocol LIKE \"" + protocol + "\""
        statement += ")"
        qstatement.append(statement)
    
    if greps:
        statement = "AND (message LIKE \"%" + \
                greps[0] + "%\""
        for grep in greps[1:]:
            statement += " OR message LIKE \"%" + grep + "%\""
        statement += ")"
        qstatement.append(statement)

    # Filter out attributes
    if rsourcehosts:
        statement = "AND (source_host NOT LIKE \"" + \
                rsourcehosts[0] + "\""
        for host in rsourcehosts[1:]:
            statement += " AND source_host NOT LIKE \"" + host + "\""
        statement += ")"
        qstatement.append(statement)

    if rsourceports:
        statement = "AND (source_port NOT LIKE \"" + \
                rsourceports[0] + "\""
        for port in rsourceports[1:]:
            statement += " AND source_port NOT LIKE \"" + port + "\""
        statement += ")"
        qstatement.append(statement)

    if rdesthosts:
        statement = "AND (dest_host NOT LIKE \"" + \
                rdesthosts[0] + "\""
        for host in rdesthosts[1:]:
            statement += " AND dest_host NOT LIKE \"" + host + "\""
        statement += ")"
        qstatement.append(statement)

    if rdestports:
        statement = "AND (dest_port NOT LIKE \"" + \
                rdestports[0] + "\""
        for port in rdestports[1:]:
            statement += " AND dest_port NOT LIKE \"" + port + "\""
        statement += ")"
        qstatement.append(statement)

    if rprocesses:
        statement = "AND (source_process NOT LIKE \"" + \
                rprocesses[0] + "\""
        for process in rprocesses[1:]:
            statement += " AND source_process NOT LIKE \"" + process + "\""
        statement += ")"
        qstatement.append(statement)
    
    if rpids:
        statement = "AND (source_pid NOT LIKE \"" + \
                rpids[0] + "\""
        for pid in rpids[1:]:
            statement += " AND source_pid NOT LIKE \"" + pid + "\""
        statement += ")"
        qstatement.append(statement)
    
    if rprotocols:
        statement = "AND (protocol NOT LIKE \"" + \
                rprotocols[0] + "\""
        for protocol in rprotocols[1:]:
            statement += " AND protocol NOT LIKE \"" + protocol + "\""
        statement += ")"
        qstatement.append(statement)
    
    if rgreps:
        statement = "AND (message NOT LIKE \"%" + \
                rgreps[0] + "%\""
        for grep in rgreps[1:]:
            statement += "AND message NOT LIKE \"%" + grep + "%\""
        statement += ")"
        qstatement.append(statement)


    # Connect and execute
    qstatement = " ".join(qstatement)
    con = mdb.connect(db['host'], db['user'], db['password'], db['database'])

    with con:
        cur = con.cursor(mdb.cursors.DictCursor)
        if rulequery: qstatement = 'SELECT * FROM ' + ', '.join(tables)
        
        cur.execute(qstatement)
        rows = cur.fetchall()
    
    cur.close()
    con.close()

    return qstatement, rows
