import pathlib
import sqlite3

import yaml

# Copy of the ros_metrics library module
# https://github.com/DLu/ros_metrics/blob/master/ros_metrics/metric_db.py


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class MetricDB:
    """Custom wrapper around an sqlite database with a plausibly easier-to-use API."""

    def __init__(self, key, folder='.', structure_filepath=None, structure_key=None, extension='db'):
        data_folder = pathlib.Path(folder)
        filepath = data_folder / f'{key}.{extension}'
        self.raw_db = sqlite3.connect(str(filepath), detect_types=sqlite3.PARSE_DECLTYPES)
        self.adapters = {}
        self.converters = {}
        self.register_custom_types()
        self.raw_db.row_factory = dict_factory

        if structure_filepath is None:
            if structure_key is None:
                structure_key = key

            structure_filepath = data_folder / f'{structure_key}.yaml'
        self.db_structure = yaml.safe_load(open(str(structure_filepath)))
        self._update_database_structure()

    def register_custom_types(self):
        self.register_custom_type('bool', bool, int, lambda v: bool(int(v)))

    def register_custom_type(self, name, type_, adapter_fn, converter_fn):
        self.adapters[name] = adapter_fn
        self.converters[name] = converter_fn
        sqlite3.register_adapter(type_, adapter_fn)
        sqlite3.register_converter(name, converter_fn)

    def query(self, query):
        """Run the specified query and return all the rows (as dictionaries)."""
        try:
            cursor = self.raw_db.cursor()
            cursor.execute(query)
            return cursor.fetchall()
        except sqlite3.OperationalError as e:
            print(e)
            print(query)
            raise

    def execute(self, command, params=None):
        """Execute the given command with the parameters. Return nothing."""
        try:
            cur = self.raw_db.cursor()
            if params is None:
                cur.execute(command)
            else:
                cur.execute(command, params)
            return cur
        except sqlite3.Error as e:
            print(e)
            print(command)
            print(params)
            raise

    def rename_column(self, table, old_col, new_col):
        """Rename a column in a table."""
        cols = self.db_structure['tables'][table]
        old_fields = ', '.join(cols)
        cols[cols.index(old_col)] = new_col
        new_fields = ', '.join(cols)

        self.execute(f'ALTER TABLE {table} RENAME TO {table}_x')
        types = []
        for key in cols:
            tt = self.get_field_type(key, full=True)
            types.append(f'{key} {tt}')
        type_s = ', '.join(types)
        self.execute(f'CREATE TABLE {table} ({type_s})')
        self.execute(f'INSERT INTO {table}({new_fields}) SELECT {old_fields} FROM {table}_x')
        self.execute(f'DROP TABLE {table}_x')

    def reset(self, table=None):
        """Clear all of the data out of the database and recreate the tables."""
        db = self.raw_db.cursor()
        if table is None:
            tables = list(self.db_structure['tables'].keys())
        else:
            tables = [table]
        for table in tables:
            db.execute(f'DROP TABLE IF EXISTS {table}')
        self._update_database_structure()

    def write(self):
        self.raw_db.commit()

    def close(self, print_table_sizes=True):
        """Write data to database. Possibly print the number of rows in each table."""
        if print_table_sizes:
            for table in self.db_structure['tables']:
                print('{}({})'.format(table, self.count(table)))
        self.write()
        self.raw_db.close()

    # Convenience interfaces for special types of queries
    def lookup_all(self, field, table, clause=''):
        """Run a SELECT command with the specified field, table and clause, return an array of the matching values."""
        values = []
        for row in self.query(f'SELECT {field} from {table} {clause}'):
            values.append(row[field])
        return values

    def lookup(self, field, table, clause=''):
        """Run a SELECT command and return the first (only?) value."""
        results = self.lookup_all(field, table, clause + ' LIMIT 1')
        if not results:
            return None
        return results[0]

    def count(self, table, clause=''):
        """Return the number of results for a given query."""
        return self.lookup('count(*)', table, clause)

    def dict_lookup(self, key_field, value_field, table, clause=''):
        """Return a dictionary mapping the key_field to the value_field for some query."""
        results = self.query(f'SELECT {key_field}, {value_field} FROM {table} {clause}')
        return {d[key_field]: d[value_field] for d in results}

    def unique_counts(self, table, ident_field):
        """Return a dictionary mapping the different values of the ident_field column to how many times each appears."""
        return self.dict_lookup(ident_field, 'count(*)', table, 'GROUP BY ' + ident_field)

    def sum_counts(self, table, value_field, ident_field):
        """Return the values of the ident_field column mapped to the sum of the value_field column."""
        return self.dict_lookup(ident_field, f'sum({value_field})', table, 'GROUP BY ' + ident_field)

    # Convenience interfaces for inserting or updating a dictionary row into the table
    def insert(self, table, row_dict, replace_key=None):
        """Insert the given row into the table. If replace_key is specified, update the row with matching key."""
        keys = row_dict.keys()

        values = []
        for k in keys:
            value = row_dict.get(k)
            values.append(value)
        key_s = ', '.join(keys)
        q_s = ', '.join(['?'] * len(values))

        cur = self.execute(f'INSERT INTO {table} ({key_s}) VALUES({q_s})', values)
        return cur.lastrowid

    def update(self, table, row_dict, replace_key='id'):
        """If there's a row where the key value matches the row_dict's value, update it. Otherwise, insert it."""
        if isinstance(replace_key, str):
            clause = 'WHERE {}={}'.format(replace_key,
                                          self.format_value(replace_key, row_dict[replace_key]))
        else:
            clause = 'WHERE {}'.format(' and '.join(['{}={}'.format(key,
                                                                    self.format_value(key, row_dict[key]))
                                                     for key in replace_key]))
        if self.count(table, clause) == 0:
            # If no matches, just insert
            return self.insert(table, row_dict)

        v_query = []
        values = []
        for k in row_dict.keys():
            if k == replace_key:
                continue
            values.append(row_dict[k])
            v_query.append(f'{k}=?')
        value_str = ', '.join(v_query)
        query = f'UPDATE {table} SET {value_str} ' + clause
        cur = self.execute(query, values)
        return cur.lastrowid

    def get_next_id(self, table, start_id=0):
        """Return an id that is not yet in the table."""
        all_ids = self.lookup_all('id', table)
        next_id = start_id
        while next_id in all_ids:
            next_id += 1
        return next_id

    def get_entry_id(self, table, values):
        """If the given values are in a table, return the id. Otherwise assign a new id and insert values."""
        clause_parts = []
        for k, v in values.items():
            clause_parts.append('{}={}'.format(k, self.format_value(k, v)))
        clause = ' and '.join(clause_parts)
        entry_id = self.lookup('id', table, f'WHERE {clause}')
        if entry_id is None:
            entry_id = self.get_next_id(table)
            values['id'] = entry_id
            self.insert(table, values)
        return entry_id

    # DB Structure Operations
    def get_field_type(self, field, full=False):
        """Return the type of a given field, based on the db_structure."""
        base = self.db_structure['special_types'].get(field, self.db_structure.get('default_type', 'text'))
        if not full or field != 'id':
            return base
        else:
            return base + ' PRIMARY KEY'

    def format_value(self, field, value):
        """If the field's type is text, surround with quotes."""
        ft = self.get_field_type(field)
        if ft == 'text':
            if not isinstance(value, str):
                value = str(value)
            if '"' in value:
                if "'" in value:
                    return '"{}"'.format(value.replace('"', '""'))
                else:
                    return f"'{value}'"
            else:
                return f'"{value}"'
        elif ft in self.adapters:
            return self.adapters[ft](value)
        else:
            return value

    def _table_exists(self, table):
        """Return a boolean of whether the table exists."""
        return self.count('sqlite_master', f"WHERE type='table' AND name='{table}'") > 0

    def _create_table(self, table):
        """Create the table based on the db_structure."""
        types = []
        for key in self.db_structure['tables'][table]:
            tt = self.get_field_type(key, full=True)
            types.append(f'{key} {tt}')
        type_s = ', '.join(types)
        self.execute(f'CREATE TABLE {table} ({type_s})')

    def _table_types(self, table):
        """Return a dictionary mapping the name of each field in a table to its type (according to the db)."""
        type_map = {}
        for row in self.query(f'PRAGMA table_info("{table}")'):
            type_map[row['name']] = row['type']
        return type_map

    def _update_table(self, table):
        """Update the structure of an existing table (as needed)."""
        type_map = self._table_types(table)
        for key in self.db_structure['tables'][table]:
            tt = self.get_field_type(key)
            if key not in type_map:
                self.execute(f'ALTER TABLE {table} ADD COLUMN {key} {tt}')

    def _update_database_structure(self):
        """Create or update the structure of all tables."""
        for table, keys in self.db_structure['tables'].items():
            if not self._table_exists(table):
                self._create_table(table)
            else:
                self._update_table(table)
