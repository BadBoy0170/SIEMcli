#!/usr/bin/env python

   

from siemcli import __version__
import os
from time import strftime
from argparse import ArgumentParser
import ConfigParser
import siemcli.query
import json



class QueryCore:

    def __init__(self):
        """Initialize live parser"""

        self.args = None
        self.arg_parser = ArgumentParser()
        self.query_args = self.arg_parser.add_argument_group('query options')
        self.config = None

        self.db = {}
        self.tables = []
        self.displayfields = None



    def get_args(self):
        """Set argument options"""

        self.arg_parser.add_argument('--version', action = 'version',
                version = '%(prog)s ' + str(__version__))
        self.arg_parser.add_argument('-c',
                action = 'store', dest = 'config',
                default = '/etc/siemcli/db.conf',
                help = ('set the config file'))
        self.arg_parser.add_argument('-s',
                action = 'store', dest = 'section',
                default = 'siem_default',
                help = ('set the config section'))
        self.arg_parser.add_argument('--verbose',
                action = 'store_true', dest = 'verbose',
                help = ('print SQL statement used for query'))
        self.arg_parser.add_argument('--silent',
                action = 'store_true', dest = 'silent',
                help = ('silence table output to terminal'))
        self.arg_parser.add_argument('--rule',
                action = 'store_true', dest = 'rule',
                help = ('set rule query mode'))
        self.arg_parser.add_argument('--json',
                action = 'store', dest = 'outjson',
                metavar= 'FILE',
                help = ('set a JSON output file'))
        self.query_args.add_argument('--table',
                action = 'append', dest = 'tables',
                metavar = 'TABLE',
                help = ('set a table to query'))
        self.query_args.add_argument('--last',
                action = 'store', dest = 'last', default = '24h',
                help = ('match a preceeding time range (5m, 24h, etc)'))
        self.query_args.add_argument('--range',
                action = 'store', dest = 'range',
                metavar = 'START-FINISH',
                help = ('match a date range (format: YYmmddHHMMSS)'))
        self.query_args.add_argument('--id',
                action = 'append', dest = 'ids',
                metavar = 'ID',
                help = ('match an event ID'))
        self.query_args.add_argument('--shost',
                action = 'append', dest = 'shosts',
                metavar = 'HOST',
                help = ('match a source host'))
        self.query_args.add_argument('--sport',
                action = 'append', dest = 'sports',
                metavar = 'PORT',
                help = ('match a source port'))
        self.query_args.add_argument('--dhost',
                action = 'append', dest = 'dhosts',
                metavar = 'HOST',
                help = ('match a destination host'))
        self.query_args.add_argument('--dport',
                action = 'append', dest = 'dports',
                metavar = 'PORT',
                help = ('match a destination port'))
        self.query_args.add_argument('--process',
                action = 'append', dest = 'processes',
                metavar = 'PROCESS',
                help = ('match a source process'))
        self.query_args.add_argument('--pid',
                action = 'append', dest = 'pids',
                metavar = 'pid',
                help = ('match a source process ID'))
        self.query_args.add_argument('--protocol',
                action = 'append', dest = 'protocols',
                metavar = 'PROTOCOL',
                help = ('match a protocol'))
        self.query_args.add_argument('--grep',
                action = 'append', dest = 'greps',
                metavar = 'PATTERN',
                help = ('match a pattern'))
        self.query_args.add_argument('--rshost',
                action = 'append', dest = 'rshosts',
                metavar = 'HOST',
                help = ('filter out a source host'))
        self.query_args.add_argument('--rsport',
                action = 'append', dest = 'rsports',
                metavar = 'PORT',
                help = ('filter out a source port'))
        self.query_args.add_argument('--rdhost',
                action = 'append', dest = 'rdhosts',
                metavar = 'HOST',
                help = ('filter out a destination host'))
        self.query_args.add_argument('--rdport',
                action = 'append', dest = 'rdports',
                metavar = 'PORT',
                help = ('filter out a destination port'))
        self.query_args.add_argument('--rprocess',
                action = 'append', dest = 'rprocesses',
                metavar = 'PROCESS',
                help = ('filter out a source process'))
        self.query_args.add_argument('--rpid',
                action = 'append', dest = 'rpids',
                metavar = 'pid',
                help = ('filter out a source process ID'))
        self.query_args.add_argument('--rprotocol',
                action = 'append', dest = 'rprotocols',
                metavar = 'PROTOCOL',
                help = ('filter out a protocol'))
        self.query_args.add_argument('--rgrep',
                action = 'append', dest = 'rgreps',
                metavar = 'PATTERN',
                help = ('filter out a pattern'))

        self.arg_parser.add_argument_group(self.query_args)
        self.args = self.arg_parser.parse_args()



    def get_config(self):
        """Read the config file"""

        config = ConfigParser.ConfigParser()
        if os.path.isfile(self.args.config):
            myconf = (config)
        else: myconf = 'config/db.conf'
        config.read(myconf)

        self.db['host'] = config.get('siemcli', 'server')
        self.db['user'] = config.get('siemcli', 'user')
        self.db['password'] = config.get('siemcli', 'password')
        self.db['database'] = config.get('siemcli', 'database')
        sectionfile = config.get('siemcli', 'sectionfile')

        if not sectionfile.startswith('/'):
            sectionfile = \
                    '/'.join(os.path.abspath(myconf).split('/')[:-1]) + \
                    '/' + sectionfile

        config.read(sectionfile)
        
        if self.args.tables:
            self.tables = self.args.tables
        else:
            self.tables.append(config.get(self.args.section, 'table'))
        try:
            self.displayfields = [x for x in config.get(
                self.args.section, 'displayfields').split(',')]
        except ConfigParser.NoSectionError:
            self.displayfields = ['id', 'date_stamp', 'source_host', 
                    'process', 'pid', 'message']



    def clear_siem(self):
        """Clear SQL table specified in section"""

        con = mdb.connect(self.db['host'], self.db['user'],
                self.db['password'], self.db['database'])

        with con:
            cur = con.cursor()

            cur.execute('DROP TABLE IF EXISTS ' + self.table)

        cur.close()
        con.close()



    def query_siem(self):
        """Query SQL database for log events"""
        
        qstatement, rows = siemcli.query.query(self.db,
                tables = self.tables,
                last = self.args.last,
                daterange = self.args.range,
                ids = self.args.ids,
                sourcehosts = self.args.shosts,
                sourceports = self.args.sports,
                desthosts = self.args.dhosts,
                destports = self.args.dports,
                processes = self.args.processes,
                pids = self.args.pids,
                protocols = self.args.protocols,
                greps = self.args.greps,
                rsourcehosts = self.args.rshosts,
                rsourceports = self.args.rsports,
                rdesthosts = self.args.rdhosts,
                rdestports = self.args.rdports,
                rprocesses = self.args.rprocesses,
                rpids = self.args.rpids,
                rprotocols = self.args.rprotocols,
                rgreps = self.args.rgreps,
                rulequery = self.args.rule)


        if self.args.verbose: print("SQL:\n" + qstatement)

        if not self.args.silent:
            print("%9s %20s %18s %14s %10s %10s %s" % (
                    self.displayfields[0],
                    self.displayfields[1],
                    self.displayfields[2],
                    self.displayfields[3],
                    self.displayfields[4],
                    self.displayfields[5],
                    self.displayfields[6]))
                   
            for row in rows:
                print("%9s %20s %18s %14s %10s %10s %s" % (
                        row[self.displayfields[0]],
                        row[self.displayfields[1]],
                        row[self.displayfields[2]],
                        row[self.displayfields[3]],
                        row[self.displayfields[4]],
                        row[self.displayfields[5]],
                        row[self.displayfields[6]]))

        if self.args.outjson:
            jrows = []
            for row in rows:
                # To Do: update fractional datestamps
                jrow = row
                if 'date_stamp_int' in jrow:
                    jrow['date_stamp_int'] = \
                            jrow['date_stamp_int'].strftime('%Y%m%d%H%M%S')
                if 'date_stamp' in jrow:
                    try:
                        jrow['date_stamp'] = \
                                jrow['date_stamp'].strftime(
                                        '%Y%m%d%H%M%S.%f')
                    except Exception:
                        if 'date_stamp_int' in jrow:
                            jrow['date_stamp'] = jrow['date_stamp_int']
                if 'date_stamp_utc_int' in jrow:
                    jrow['date_stamp_utc_int'] = \
                            jrow['date_stamp_utc_int'].strftime(
                                    '%Y%m%d%H%M%S')
                if 'date_stamp_utc' in jrow:
                    try:
                        jrow['date_stamp_utc'] = \
                                jrow['date_stamp_utc'].strftime(
                                        '%Y%m%d%H%M%S.%f')
                    except Exception:
                        if 'date_stamp_utc_int' in jrow:
                            jrow['date_stamp_utc'] = \
                                    jrow['date_stamp_utc_int']
                if 'extended' in jrow:
                    jrow['extended'] = json.loads(jrow['extended'])
                jrows.append(jrow)

            with open(self.args.outjson, 'w') as f:
                f.write(json.dumps(rows, indent=2, sort_keys=True,
                    separators=(',', ': ')) + '\n')
                   
                   
                   
    def run_query(self):
        try:
            self.get_args()
            self.get_config()
            self.query_siem()

        except KeyboardInterrupt:
            pass
        # except Exception as err:
        #     print('Error: ' + str(err))

    
    
def main():
    query = QueryCore()
    query.run_query()


if __name__ == "__main__":
    query = QueryCore()
    query.run_query()
