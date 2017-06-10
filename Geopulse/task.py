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
from psycopg2 import sql
import pandas as pd

"""
Resources:
http://initd.org/psycopg/docs/index.html
"""

# TODO: How to define a string
# TODO: http://initd.org/psycopg/docs/usage.html#the-problem-with-the-query-parameters


class DataBase:
    # available types from http://www.postgresqltutorial.com/postgresql-data-types/
    AVAILABLE_COLUMN_TYPES = ['int', 'smallint', 'real', 'integer',
                              'text',
                              'bool',
                              'timestamp',
                              'SERIAL'
                              ]
    # TODO: other column types can be added, see http://www.postgresqltutorial.com/postgresql-data-types/

    # mapping of column types to the value validation instance
    COLUMN_TYPE_INSTANCE_MAPPING = {
        'integer': int,
        'text': str,
        # TODO: add others
    }

    def __init__(self, dbname, user, password):
        self.connection = psycopg2.connect("dbname={} user={} password={}".format(dbname, user, password))
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

        # assert table name is valid - lowercase, no numbers \ special characters
        assert all([char.isalpha() or char == '_' for char in table_name]), \
            'table name should only contain letters or underscore (_)'
        table_name = table_name.lower()

        # fill in command string
        command_string = "CREATE TABLE {} (".format(table_name)

        for ix, (col_name, col_type) in enumerate(column_names_types.items()):
            # assert column type is valid
            assert col_type in self.AVAILABLE_COLUMN_TYPES, \
                'Invalid type for column: {}, got {}, expected one of {}'.format(
                    col_name, col_type, self.AVAILABLE_COLUMN_TYPES)

            # add column name and type to string
            name_value_pair = "{} {}{}".format('_' + col_name if col_type == 'SERIAL' else col_name,  # add '_' to serial to help differentiate
                                               col_type,
                                               ' PRIMARY KEY' if col_type == 'SERIAL' else '')  # serial columns should be primary keys
            command_string += name_value_pair

            # add space and comma for all columns except the last
            if ix < len(column_names_types)-1:
                command_string += ', '

        # close the command string
        command_string += ');'

        # escape all special characters before executing query
        command_string = self.cursor.mogrify(command_string)
        self.cursor.execute(command_string)

        if make_persistent:
            self.connection.commit()

    def delete_table(self, table_name, make_persistent=True):
        """
        Deletes (drops) table if it exists.
        :param table_name:
        """

        self.cursor.execute(self.cursor.mogrify("DROP TABLE IF EXISTS {}".format(table_name)))

        if make_persistent:
            self.connection.commit()

    def _get_column_names_types(self, table_name):
        self.cursor.execute("SELECT column_name, data_type from INFORMATION_SCHEMA.Columns WHERE table_name = \'{}\'".format(table_name))
        return dict(self.cursor.fetchall())

    def _validate_values_for_columns(self, table_name, **column_names_values):
        """
        Validates provided values are of same type as column expects
        :param table_name:
        :param column_names_values:
        :return:
        """
        # get column names and types for current table
        column_names_types = self._get_column_names_types(table_name)

        for col_name, col_value in column_names_values.items():
            col_type = column_names_types[col_name]
            assert isinstance(col_value, self.COLUMN_TYPE_INSTANCE_MAPPING[col_type]), \
                'Value mismatch in {}, expected {}, got {} ({})'.format(col_name, col_type,
                                                                        col_value,
                                                                        type(col_value).__name__)

    def add_row(self, table_name, make_persistent=True, **column_names_values):
        """
        Adds row to table.
        :param table_name:
        :param make_persistent:
        :param column_names_values:
        :return:
        """

        self._validate_values_for_columns(table_name, **column_names_values)
        column_names_types = self._get_column_names_types(table_name)

        # validate values and create lists for command string
        column_names = [col_name for col_name in column_names_types.keys() if col_name[0] != '_']
        column_values = []
        for col_name in column_names:
            if col_name in column_names_values:
                # user provided value for this column, validate value
                col_type = column_names_types[col_name]  # get column type
                user_provided_value = column_names_values[col_name]
                assert isinstance(user_provided_value, self.COLUMN_TYPE_INSTANCE_MAPPING[col_type]), \
                    'Value mismatch in {}, expected {}, got {} ({})'.format(col_name, col_type,
                                                                            user_provided_value,
                                                                            type(user_provided_value).__name__)
                column_values.append(user_provided_value)
            else:
                # user did not provide this value, set it as None (Null in db)
                column_values.append(None)

        column_names_string = ', '.join(column_names)
        placeholders_string = ['%s'] * len(column_names)
        placeholders_string = ', '.join(placeholders_string)
        command_string = "INSERT INTO {} ({}) VALUES ({})".format(table_name, column_names_string, placeholders_string)
        self.cursor.execute(self.cursor.mogrify(command_string, tuple(column_values)))

        if make_persistent:
            self.connection.commit()

    def query_table(self, table_name, query=None, column_names='*'):
        """
        :param table_name: string, table name
        :param query: sql string
        :param column_names: string \ list of strings to only get some columns from table
        :return: Pandas DataFrame of the result
        """
        # TODO: Maybe will be easier for user to not use SQL syntax in query, but this may require defining filters
        # TODO: and parsing user inputs, which will not be done at this stage.

        # TODO: The current implementation does not support JOIN syntax.
        # TODO: To allow this, we should parse the user query for the JOIN keyword, run query_table on all tables in
        # TODO: JOIN separately and then join them according to the relevant columns (concatenate columns of multiple
        # TODO: Pandas DataFrames, according to matching columns (without duplications).

        existing_column_names = self._get_column_names_types(table_name).keys()

        if column_names != '*':
            if not isinstance(column_names, (list, tuple)):
                column_names = [column_names]
            for col_name in column_names:
                assert col_name in existing_column_names, 'Column {} does not exist in Table {}'.format(col_name, table_name)

        cols_to_show = column_names if column_names == '*' else ', '.join(column_names)
        command_string = "SELECT {} FROM {}".format(cols_to_show, table_name)

        if query is None:
            command_string += ';'
        else:
            command_string += ' WHERE {} ;'.format(query)

        self.cursor.execute(self.cursor.mogrify(command_string))
        res = self.cursor.fetchall()
        cols_for_dataframe = existing_column_names if column_names == '*' else cols_to_show.split(', ')
        res_dict = {key: values for key, values in zip(cols_for_dataframe, zip(*res))}
        return pd.DataFrame(data=res_dict)
        # in this case, both _id and pandas index columns are available.
        #  we can overwrite the pandas index (pd.DataFrame(data=res_dict, index=res_dict['_id'])), but then we should
        # also remove _id column from res_dict before assignment do dDataFrame

'''
    def _get_serial_column_from_table(self, table_name):
        """
        Returns name of the serial column from table_name.
        https://wiki.postgresql.org/wiki/Retrieve_primary_key_columns
        """

        # TODO: this doesn't work for db.create_table('table_one', id='SERIAL', num='integer', word='text')
        # TODO: for now, serial columns will be marked with _ in the beginning. id --> _id.

        command_string = """SELECT a.attname, format_type(a.atttypid, a.atttypmod) AS data_type FROM pg_index i
         JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey) WHERE i.indrelid = '{}'::regclass""".format(table_name)

        return self.cursor.execute(self.cursor.mogrify(command_string))
'''