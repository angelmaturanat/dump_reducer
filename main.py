
# -*- coding: utf-8 -*-

import os
import subprocess
import argparse
import logging
import calendar
import time
import json

from mysql.connector import connect, Error

# Configure Logging
logging.basicConfig(
    format='[%(levelname)s][%(asctime)s]: %(message)s', level=logging.INFO)
log = logging.getLogger(__name__)

class Rules(object):
    def __init__(self):
        pass

    def get_rules():
        rules_file = open('rules.json')
        rules = json.load(rules_file)

        return sorted(rules, key=lambda i: i['priority_number'] if i['priority_number'] is not None else 999999)

class Interpreter(object):
    def __init__(self, params={}):
        self.params = params

    def run(self):
        rules = Rules.get_rules()
        params = self.params

        conn = self.db_connect(params)
        db_name = params.get(
            'database') + '_' + str(calendar.timegm(time.gmtime()))

        self._create_dump_file(params, db_name)

        self._create_db(conn, db_name)
        self._restore_dump(params, db_name)

        self.process_rules(conn, params, db_name, rules)

    def _execute_previous_query(self, conn, rule):
        if rule['previous_exectution'] is not None:
            cur = conn.cursor(buffered=True)
            cur.execute(rule['previous_exectution'])
            conn.commit()

    def process_rules(self, conn, params, db_name, rules):
        for rule in rules:
            print('Processing ' + rule['table'] + ' table')

            if rule['raw_source'] is not None:
                query_stmt = 'INSERT IGNORE INTO {target_database}.{table} '.format(
                    source_table=params['database'],
                    target_database=db_name,
                    table=rule['table']
                ) + rule['raw_source']
            else:
                query_stmt = 'INSERT IGNORE INTO {target_database}.{table} SELECT * FROM {source_table}.{table}'.format(
                    source_table=params['database'],
                    target_database=db_name,
                    table=rule['table']
                )

            if rule['condition'] is not None:
                query_stmt += ' ' + rule['condition']

            print(query_stmt)

            cur = conn.cursor(buffered=True)
            cur.execute(query_stmt)
            conn.commit()


    def db_connect(self, params):
        mysql_config = {
            'database': params.get('database'),
            'user': params.get('username'),
            'password': params.get('password'),
            'host': params.get('host'),
            'port': params.get('port'),
            'ssl_disabled': True
        }

        try:
            conn = connect(**mysql_config)
            if conn.is_connected():
                print('connected to database')

                return conn

        except Error as e:
            print("mysql DB connection error")
            print(e)


    def _create_db(self, conn, db_name):
        cur = conn.cursor(buffered=True)
        cur.execute("CREATE DATABASE " + db_name)


    def _restore_dump(self, params, db_name):
        dump_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), 'dump.sql'))

        cmd = ' '.join([
            "mysql",
            "--max_allowed_packet=512M",
            "--default-character-set=utf8",
            "--ssl-mode=DISABLED",
            "--host={}".format(params.get('host')),
            "--port={}".format(params.get('port')),
            "--user={}".format(params.get('username')),
            "--password={}".format(params.get('password')),
            db_name,
            "<",
            dump_path
        ])

        output = subprocess.call(cmd, shell=True)

    def _create_dump_file(self, params, db_name):
        args = [
            "mysqldump",
            "--host={}".format(params.get('host')),
            "--port={}".format(params.get('port')),
            "--user={}".format(params.get('username')),
            "--password={}".format(params.get('password')),
            "--no-data",
            "--no-create-db",
            "--default-character-set=utf8",
            "--column-statistics=0",
            "--ssl-mode=DISABLED",
            "--databases",
            params.get('database'),
            "| sed -e '/^CREATE DATABASE/d' -e '/^USE `/d'"
            "> dump.sql"
        ]

        cmd = ' '.join(args)
        return subprocess.call(cmd, shell=True)

    @classmethod
    def get_parser(cls):
        parser = argparse.ArgumentParser()
        parser.add_argument("--host", help="MySQL server host", required=True)
        parser.add_argument("--username", help="MySQL server user", required=True)
        parser.add_argument("--password", help="MySQL password", default="")
        parser.add_argument("--database", help="Database name", required=True)
        parser.add_argument("--port", help="MySQL port",
                            type=int, required=False, default=3306)

        return parser

    @classmethod
    def define_params_from_args(cls, args):
        params = {
            'host': args.host,
            'username': args.username,
            'password': args.password,
            'database': args.database,
            'port': args.port
        }

        return params

    @classmethod
    def main(cls):
        parser = cls.get_parser()
        args = parser.parse_args()
        params = cls.define_params_from_args(args)
        r = cls(params)
        r.run()

if __name__ == '__main__':
    # Command line arguments parser
    log.info('Starting script...')

    Interpreter.main()
