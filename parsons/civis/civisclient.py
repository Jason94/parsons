import civis
import os
from parsons.etl.table import Table


class CivisClient(object):

    def __init__(self, db=None, api_key=None):

        if api_key is None:

            try:
                self.api_key = os.environ['CIVIS_API_KEY']
            except KeyError:
                raise KeyError('No Civis API key found. Please store'
                               ' in environment variable or pass as an'
                               'argument.')

        if db is None:
            try:
                db = os.environ['CIVIS_DATABASE']
            except KeyError:
                raise KeyError('No Civis Database kwarg found. Please store'
                               ' in environment variable or pass as an'
                               'argument.')

        if str(db).isdigit():
            db = int(db)

        self.db = db

        if api_key:
            os.environ['CIVIS_API_KEY'] = api_key

    def query(self, sql, preview_rows=10, polling_interval=None, hidden=True,
              wait=True):
        """Execute a SQL statement as a Civis query.

        Run a query that may return no results or where only a small
        preview is required. To execute a query that returns a large number
        of rows, see :func:`~civis.io.read_civis_sql`.

        `Args`
            sql: str
                The SQL statement to execute.
            preview_rows: int, optional
                The maximum number of rows to return. No more than 100 rows can be
                returned at once.
            polling_interval: int or float, optional
                Number of seconds to wait between checks for query completion.
            hidden: bool, optional
                If ``True`` (the default), this job will not appear in the Civis UI.
            wait: boolean
                If ``True``, will wait for query to finish executing before exiting
                the method.
        `Returns`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        fut = civis.io.query_civis(sql, self.db, preview_rows=preview_rows, polling_interval=None)

        if not wait:

            return None

        result = fut.result()

        if result['result_rows'] is None:

            return None

        result['result_rows'].insert(0, result['result_columns'])

        return Table(result['result_rows'])

    def table_import(self, table_obj, table, max_errors=None,
                     existing_table_rows='fail', diststyle=None, distkey=None,
                     sortkey1=None, sortkey2=None, wait=True, **civisargs):
        """
        Write the table to a Civis Redshift cluster. Additional key word
        arguments can passed to `civis.io.dataframe_to_civis()  <https://civis-python.readthedocs.io/en/v1.9.0/generated/civis.io.dataframe_to_civis.html#civis.io.dataframe_to_civis>`_ # noqa: E501

        `Args`
            table_obj: obj
                A Parsons Table object
            table: str
                The schema and table you want to upload to. E.g., 'scratch.table'. Schemas
                or tablenames with periods must be double quoted, e.g. 'scratch."my.table"'.
            api_key: str
                Your Civis API key. If not given, the CIVIS_API_KEY environment variable will be
                used.
            max_errors: int
                The maximum number of rows with errors to remove from the import before failing.
            existing_table_rows: str
                The behaviour if a table with the requested name already exists. One of
                `'fail'`, `'truncate'`, `'append'` or `'drop'`. Defaults to `'fail'`.
            diststyle: str
                The distribution style for the table. One of `'even'`, `'all'` or `'key'`.
            distkey: str
                The column to use as the distkey for the table.
            sortkey1: str
                The column to use as the sortkey for the table.
            sortkey2: str
                The second column in a compound sortkey for the table.
            wait: boolean
                Wait for write job to complete before exiting method.
        `Returns`
            ``None``
        """

        fut = civis.io.dataframe_to_civis(table_obj.to_dataframe(), database=self.db,
                                          table=table, max_errors=max_errors,
                                          existing_table_rows=existing_table_rows,
                                          diststyle=diststyle, distkey=distkey,
                                          sortkey1=sortkey1, sortkey2=sortkey2,
                                          headers=True, **civisargs)

        if wait:

            fut.result()