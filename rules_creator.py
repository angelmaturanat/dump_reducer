
# -*- coding: utf-8 -*-

import argparse
import logging
import json

from mysql.connector import connect, Error

# Configure Logging
logging.basicConfig(
    format='[%(levelname)s][%(asctime)s]: %(message)s', level=logging.INFO)
log = logging.getLogger(__name__)

class RulesCreator(object):
    def __init__(self, params={}):
        self.params = params

    def run(self):
        params = self.params

        conn = self.db_connect(params)
        tables = self.get_db_tables(conn)

        self.create_rules_file(tables, params)


    def create_rules_file(self, tables, params):
        rules = list()
        custom_condition = params.get('condition', None)

        for table in tables:
            rules.append({
                "table": table[0],
                "raw_source": None,
                "condition": custom_condition,
                "priority_number": None
            })

        if rules:
            file = open('rules.json', 'w')
            file.write(json.dumps(rules))
            file.close()


    def get_db_tables(self, conn):
        tables = conn.cursor(buffered=True)
        tables.execute("SHOW TABLES")

        return tables

        for table_name in cur:
            print(table_name[0])

        exit()

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

    @classmethod
    def get_parser(cls):
        parser = argparse.ArgumentParser()
        parser.add_argument("--host", help="MySQL server host", required=True)
        parser.add_argument("--username", help="MySQL server user", required=True)
        parser.add_argument("--password", help="MySQL password", default="")
        parser.add_argument("--database", help="Database name", required=True)
        parser.add_argument("--port", help="MySQL port",
                            type=int, required=False, default=3306)
        parser.add_argument("--condition", help="Custom Where condition", required=False)

        return parser

    @classmethod
    def define_params_from_args(cls, args):
        params = {
            'host': args.host,
            'username': args.username,
            'password': args.password,
            'database': args.database,
            'port': args.port,
            'condition': args.condition
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

    RulesCreator.main()
