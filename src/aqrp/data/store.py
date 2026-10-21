"""DuckDB is a disposable index over verified immutable Parquet, never authority."""

import duckdb

from .snapshot import verify_snapshot


def read_snapshot(ref):
    manifest, tables = verify_snapshot(ref)
    result = {}
    with duckdb.connect(":memory:") as connection:
        connection.execute("SET TimeZone='UTC'")
        for name, table in tables.items():
            connection.register("input_table", table)
            connection.execute("CREATE OR REPLACE TABLE verified AS SELECT * FROM input_table")
            result[name] = (
                connection.execute("SELECT * FROM verified").to_arrow_table().cast(table.schema)
            )
            connection.unregister("input_table")
    return manifest, result
