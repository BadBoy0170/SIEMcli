#!/usr/bin/env python

   

import time
from time import strftime
from time import sleep
from time import daylight
from time import timezone
from time import altzone
from random import randrange
from datetime import datetime
import MySQLdb as mdb
import json
import threading
import os
from sys import exit
import siemcli.manage
#import signal


class SiemTrigger:

    def __init__(self, db, rule):
        """Initialize trigger object"""
        
        self.db = db
        self.rule = rule
        self.tzone = None



    def watch_rule(self):
        """Watch a trigger rule"""

        # Set time zone:
        if daylight:
            self.tzone = \
                    str(int(float(altzone) / 60 // 60)).rjust(2,
                            '0') + \
                    str(int(float(altzone) / 60 % 60)).ljust(2, '0')
        else:
            self.tzone = \
                    str(int(float(timezone) / 60 // 60)).rjust(2,
                            '0') + \
                    str(int(float(timezone) / 60 % 60)).ljust(2, '0')
        if not '-' in self.tzone:
            self.tzone = '+' + self.tzone

        while True:

            # Check the rule:
            self.check_rule()
        
            # Wait until the next interval
            sleep(int(self.rule['time_int']) * 60)



    def check_rule(self):
        """Check a trigger rule"""
        
        # To Do: Add date_stamp_utc/int logic
        if not self.tzone:
            # Set time zone:
            if time.localtime().tm_isdst:
                self.tzone = \
                        str(int(float(altzone) / 60 // 60)).rjust(2,
                                '0') + \
                        str(int(float(altzone) / 60 % 60)).ljust(2, '0')
            else:
                self.tzone = \
                        str(int(float(timezone) / 60 // 60)).rjust(2,
                                '0') + \
                        str(int(float(timezone) / 60 % 60)).ljust(2, '0')
            if not '-' in self.tzone:
                self.tzone = '+' + self.tzone

        # Query the database:
        con = mdb.connect(self.db['host'], self.db['user'],
                self.db['password'], self.db['database'])
        with con:
            cur = con.cursor()
            cur.execute(self.rule['sql_query'])
            rows = cur.fetchall()
            cur.close()
        con.close()
    
        # Evaluate the results:
        if len(rows) > int(self.rule['event_limit']):
            idtags = json.dumps([int(row[0]) for row in rows])

            datestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            datestamputc = datetime.utcnow().strftime('%Y%m%d%H%M%S')

            magnitude = (((len(rows) // 2) // \
                    (self.rule['event_limit'] + 1) // 2) + 5) * \
                    ( 7 - self.rule['severity'])

            outstatement = 'INSERT INTO ' + \
                    self.rule['out_table'] + \
                    '(date_stamp, date_stamp_utc, t_zone, ' + \
                    'source_rule, severity, source_table, event_limit, ' + \
                    'event_count, magnitude, time_int, message, source_ids) ' + \
                    'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

            # Send an event to the database:
            con = mdb.connect(self.db['host'], self.db['user'],
                    self.db['password'], self.db['database'])
            with con:
                cur = con.cursor()
                cur.execute(outstatement, (datestamp, datestamputc,
                    self.tzone,
                    self.rule['rule_name'], self.rule['severity'],
                    self.rule['source_table'],
                    self.rule['event_limit'], len(rows), magnitude,
                    self.rule['time_int'], self.rule['message'],
                    idtags))
                cur.close()
            con.close()

def start_rule(db, rule, oneshot):
    """Initialize trigger object and start watching"""
    
    # Make sure the table exists:
    siemcli.manage.create_ruleevent_table(rule['out_table'])

    sentry = SiemTrigger(db, rule)

    if oneshot:
        sentry.check_rule()
    elif int(rule['time_int']) == 0:
        pass
    
    else:
        # Before starting, sleep randomly up to rule interval to stagger
        # database use:
        sleep(randrange(0, int(rule['time_int']) * 60))

        sentry.watch_rule()
