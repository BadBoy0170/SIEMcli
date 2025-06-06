#!/usr/bin/env python

   

from siemcli import __version__
from siemcli.manage import SIEMMgr
import time
from datetime import datetime
import re
import sys
import os
import MySQLdb as mdb
from argparse import ArgumentParser
from argparse import FileType
import ConfigParser
import json



class ManageCore:

    def __init__(self):
        """Initialize live parser"""

        self.args = None
        self.arg_parser = ArgumentParser()
        self.config = None

        self.db = {}
        self.table = None



    def get_args(self):
        """Set argument options"""

        self.arg_parser.add_argument('--version', action = 'version',
                version = '%(prog)s ' + str(__version__))
        self.arg_parser.add_argument('-c',
                action = 'store', dest = 'config',
                default = '/etc/siemcli/db.conf',
                help = ('set the config file'))
        self.arg_parser.add_argument('--clear',
                action = 'store_true', dest = 'clearsiem',
                help = ('delete the SQL table for selected section'))
        self.arg_parser.add_argument('--force',
                action = 'store_true', dest = 'force',
                help = ('really delete the table'))
        self.arg_parser.add_argument('--importrules',
                action = 'store', dest = 'importrules',
                metavar = 'FILE',
                help = ('set a JSON file to import rules'))
        self.arg_parser.add_argument('--exportrules',
                action = 'store', dest = 'exportrules',
                metavar = 'FILE',
                help = ('set a JSON file to export rules'))
        self.arg_parser.add_argument('--importhelpers',
                action = 'store', dest = 'importhelpers',
                metavar = 'FILE',
                help = ('set a JSON file to import helpers'))
        self.arg_parser.add_argument('--exporthelpers',
                action = 'store', dest = 'exporthelpers',
                metavar = 'FILE',
                help = ('set a JSON file to export helpers'))
        self.arg_parser.add_argument('--table',
                action = 'append', dest = 'tables',
                metavar = 'TABLE',
                help = ('set a table'))
        self.arg_parser.add_argument('--create-event-table',
                action = 'store', dest = 'eventtable',
                metavar = 'TABLE'
                help = ('create a table for log events'))
        self.arg_parser.add_argument('--create-ruleevent-table',
                action = 'store', dest = 'ruleeventtable',
                metavar = 'TABLE'
                help = ('create a table for log events'))
        self.arg_parser.add_argument('--create-rule-table',
                action = 'store', dest = 'ruletable',
                metavar = 'TABLE'
                help = ('create a table for log events'))
        self.arg_parser.add_argument('--create-helper-table',
                action = 'store', dest = 'helpertable',
                metavar = 'TABLE'
                help = ('create a table for log events'))

        self.args = self.arg_parser.parse_args()



    def get_config(self):
        """Read the config file"""

        config = ConfigParser.ConfigParser()
        if os.path.isfile(self.args.config):
            myconf = self.args.config
        else: myconf = 'config/db.conf'
        config.read(myconf)

        self.db['host'] = config.get('siemcli', 'server')
        self.db['user'] = config.get('siemcli', 'user')
        self.db['password'] = config.get('siemcli', 'password')
        self.db['database'] = config.get('siemcli', 'database')
        sectionfile = config.get('siemcli', 'sectionfile')

        if not sectionfile.startswith('/'):
            sectionfile = '/'.join(os.path.abspath(myconf).split('/')[:-1]) + \
                    '/' + sectionfile

        config.read(sectionfile)
        


    def run_manage(self):
        try:
            self.get_args()
            self.get_config()
            # Create tables:
            if self.args.eventtable:
                mgr = SIEMMgr(self.db)
                mgr.create_event_table(self.args.eventtable,
                        intstamps=self.args.intstamps)
            if self.args.ruleeventtable:
                mgr = SIEMMgr(self.db)
                mgr.create_ruleevent_table(self.args.ruleeventtable)
            if self.args.ruletable:
                mgr = SIEMMgr(self.db)
                mgr.create_rule_table(self.args.ruletable)
            if self.args.helpertable:
                mgr = SIEMMgr(self.db)
                mgr.create_helper_table(self.args.helpertable)
            
            # Drop tables:
            if self.args.clearsiem:
                if self.args.force:
                    mgr = SIEMMgr(self.db)
                    mgr.clear_table(self.args.tables)
                else:
                    print("Use --force option if you really want to " + \
                            "drop table (" + table + ")")
            # Rules:
            elif self.args.importrules:
                mgr = SIEMMgr(self.db)
                mgr.import_rules(self.args.importrules)
            elif self.args.exportrules:
                mgr = SIEMMgr(self.db)
                mgr.export_rules(self.args.tables,
                        self.args.exportrules)
            # Helpers:
            elif self.args.importhelpers:
                mgr = SIEMMgr(self.db)
                mgr.import_helpers(self.args.importhelpers)
            elif self.args.exporthelpers:
                mgr = SIEMMgr(self.db)
                mgr.export_helpers(self.args.tables,
                        self.args.exporthelpers)

        except KeyboardInterrupt:
            pass
        # except Exception as err:
        #     print('Error: ' + str(err))

    
    
def main():
    mgr = ManageCore()
    mgr.run_manage()


if __name__ == "__main__":
    mgr = ManageCore()
    mgr.run_manage()
