"""
We talked about having a basic environment for writing and running python code, and have it connect to a relational
database.
If you are just choosing out of the air just know that we are using postgresql.

Code should:
1. Connect to the database.
2. Create a table.
3. Add row to table.
4. Read from table.
"""

import psycopg2
import pandas as pd

"""
Resources:
http://initd.org/psycopg/docs/index.html
"""

# TODO: create a database for testing - http://www.postgresqltutorial.com/postgresql-create-database/


# TODO: How to define a string
# TODO: http://initd.org/psycopg/docs/usage.html#the-problem-with-the-query-parameters


class DataBase:
    AVAILABLE_COLUMN_TYPES = ['integer', 'varchar']  # TODO: add other available column types

    def __init__(self, dbname, user):
        self.connection = psycopg2.connect("dbname={} user={}".format(dbname, user))
        self.cursor = self.connection.cursor()

    def close(self):
        self.cursor.close()
        self.connection.close()

    def create_table(self, table_name, make_persistent=True, **column_names_types):
        """
        Creates a table.
        :param table_name: String
        :param column_names_types: Dictionary, keys are column names, values are column types.
        :param make_persistent: make changes to db persistent, True by default
        :return:
        """

        # TODO: add assertions on table name - lowercase, no spaces, no numbers, etc.

        command_string = "CREATE TABLE {}".format(table_name)

        # TODO: add assertions on column_names_types, keys lowercase, values from a set of available types

        # TODO: add column names \ types in the following format:
        # TODO: "CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);"

        self.cursor.execute(command_string)

        if make_persistent:
            self.connection.commit()

    def add_row(self, table, make_persistent=True):
        # TODO: use syntax from cur.execute("INSERT INTO test (num, data) VALUES (%s, %s)", (100, "abc'def"))
        # TODO: Note: http://initd.org/psycopg/docs/usage.html - Passing parameters to SQL queries.
        # TODO: All parameters are strings

        if make_persistent:
            self.connection.commit()

    def query_table(self, table):
        # TODO: use syntax from cur.execute("SELECT * FROM test;") \ cur.fetchone()
        # TODO: put the data into a pandas table for further processing

        df = pd.DataFrame()
        pass

    # TODO: think on how to implement join in this structure - a separate function?

# TODO: Add Table class?