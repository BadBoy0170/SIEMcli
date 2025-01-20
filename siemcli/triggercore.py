#!/usr/bin/env python

   

from siemcli import __version__
import siemcli.trigger
import threading
import os
from sys import exit
from argparse import ArgumentParser
import ConfigParser
import json
import MySQLdb as mdb
import signal
from time import sleep


class SiemTriggerCore:

    def __init__(self):
        """Initialize trigger engine"""

        self.args = None
        self.arg_parser = ArgumentParser()

        self.db = {}
        self.rules = {}
        self.threads = []

        signal.signal(signal.SIGTERM, self.sigterm_handler)


    def sigterm_handler(self, signal, frame):
        """Exit cleanly on sigterm"""
        #self.stop_threads()
        exit(0)



    def get_args(self):
        """Set argument options"""

        self.arg_parser.add_argument('--version', action = 'version',
                version = '%(prog)s ' + str(__version__))
        self.arg_parser.add_argument('-c',
                action = 'store', dest = 'config',
                default = '/etc/siemcli/db.conf',
                help = ('set the config file'))
        self.arg_parser.add_argument('--table',
                action = 'append', dest = 'tables',
                metavar = 'TABLE',
                help = ('set a rule table'))
        self.arg_parser.add_argument('--oneshot',
                action = 'store_true',
                help = ('check database once and exit'))

        self.args = self.arg_parser.parse_args()



    def get_config(self):
        """Read the config file"""

        config = ConfigParser.ConfigParser()
        if os.path.isfile(self.args.config):
            myconf = self.args.config
        else: myconf = 'config/db.conf'
        config.read(myconf)

        # Read /etc/triggers.d/*.conf in a for loop

        self.db['host'] = config.get('siemcli', 'server')
        self.db['user'] = config.get('siemcli', 'user')
        self.db['password'] = config.get('siemcli', 'password')
        self.db['database'] = config.get('siemcli', 'database')
        sectionfile = config.get('siemcli', 'sectionfile')

        if not sectionfile.startswith('/'):
            sectionfile = '/'.join(os.path.abspath(myconf).split('/')[:-1]) + \
                    '/' + sectionfile

        config.read(sectionfile)


        
    def get_rules(self):
        """Get rules from tables"""

        self.rules = []
        for table in self.args.tables:
            con = mdb.connect(self.db['host'], self.db['user'],
                    self.db['password'], self.db['database'])
            with con:
                cur = con.cursor(mdb.cursors.DictCursor)
                cur.execute('SELECT * FROM ' + table)
                rules = cur.fetchall()
                cur.close()
            con.close()
            self.rules = self.rules + list(rules)



    def start_triggers(self):
        """Start siemcli event triggers"""

        # Start one thread per rule:
        self.threads = []
        for r in self.rules:
            if r['is_enabled'] == 1:
                thread = threading.Thread(name=r,
                        target=siemcli.trigger.start_rule,
                        args=(self.db, r, self.args.oneshot))
                thread.daemon = True
                thread.start()

            self.threads.append(thread)


    def run_triggers(self):
        """Start trigger engine"""
        try:
            self.get_args()
            self.get_config()
            self.get_rules()
            self.start_triggers()

            while True:
                isAlive = False
                for thread in self.threads:
                    if thread.isAlive():
                        isAlive = True
                if not isAlive: exit(0)
                sleep(10)

        except KeyboardInterrupt:
            #self.stop_threads()
            exit(0)
        #except Exception as err:
        #    self.stop_threads()
        #    exit(0)
        #    print('Error: ' + str(err))

    
#class StoppableThread(threading.Thread):
#    def __init__(self, args):
#        super(StoppableThread, self).__init__()
#        self._stop_event = threading.Event()
#
#    def stop(self):
#        self._stop_event.set()
#
#    def stopped(self):
#        return self._stop_event.is_set()


def main():
    parser = SiemTrigger()
    parser.run_triggers()


if __name__ == "__main__":
    parser = SiemTrigger()
    parser.run_triggers()
