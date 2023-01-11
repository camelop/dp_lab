import os
import numpy as np
import sqlite3
import tempfile
import urllib.request
import jpype
import jpype.imports
from jpype.types import *

FILE_DIR = os.path.dirname(os.path.abspath(__file__))

chorus_jar_name = "chorus-0.1.3.2-SNAPSHOT-jar-with-dependencies.jar"
jar_loc = os.path.join(FILE_DIR, chorus_jar_name)
if not os.path.exists(jar_loc):
    urllib.request.urlretrieve(f"https://github.com/camelop/chorus-python/releases/download/0.1.3.2-SNAPSHOT/{chorus_jar_name}", jar_loc)

SCHEMA = """
---
databases:
- database: "default_db"
  dialect: "hive"
  namespace: ""
  tables:
  - table: "t"
    columns:
    - name: "v"
"""

jpype.startJVM("--add-opens=java.base/java.nio=ALL-UNNAMED", classpath=[jar_loc])
from chorus.integration import QueryWithDP

from dplab.library_workload.util import read_input_file, workload_main


def evaluate(query, input_file, eps, quant, lb, ub, repeat):
    data = read_input_file(input_file)
    assert lb is None and ub is None, "Chorus does not support specified bounds."
    with tempfile.NamedTemporaryFile() as tmp_db, tempfile.NamedTemporaryFile() as tmp_schema:
        conn = sqlite3.connect(tmp_db.name)
        c = conn.cursor()
        c.execute("CREATE TABLE t (v REAL)")
        c.executemany("INSERT INTO t VALUES (?)", [(d,) for d in data])
        conn.commit()
        conn.close()
        tmp_schema.write(SCHEMA.encode())
        tmp_schema.flush()

        results = []
        for i in range(repeat):
            if query == "count":
                result = QueryWithDP(tmp_db.name, tmp_schema.name, "SELECT COUNT(v) FROM t", "LaplaceMechClipping", eps, l, u).run()
            elif query == "sum":
                result = QueryWithDP(tmp_db.name, tmp_schema.name, "SELECT SUM(v) FROM t", "LaplaceMechClipping", eps, l, u).run()
            elif query == "mean":
                result = QueryWithDP(tmp_db.name, tmp_schema.name, "SELECT AVG(v) FROM t", "AverageMechClipping", eps, l, u).run()
            elif query == "var":
                raise NotImplementedError("Chorus(0.1.3) does not support var.")
            elif query == "median":
                raise NotImplementedError("Chorus(0.1.3) does not support median.")
            elif query == "quantile":
                raise NotImplementedError("Chorus(0.1.3) does not support quantile.")
            else:
                raise ValueError("Unknown query: {}".format(query))
            results.append(result)
        return results


if __name__ == "__main__":
    workload_main(evaluate)
