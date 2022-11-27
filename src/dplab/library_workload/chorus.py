import os
import numpy as np
import sqlite3
import tempfile
import jpype
import jpype.imports
from jpype.types import *

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
jpype.startJVM("--add-opens=java.base/java.nio=ALL-UNNAMED", classpath=[f'{FILE_DIR}/../../../chorus-0.1.3.2-SNAPSHOT-jar-with-dependencies.jar'])
SCHEMA_FILE = f'{FILE_DIR}/../../../data/1.schema.yaml'
from chorus.integration import QueryWithDP

from dplab.library_workload.util import read_input_file, workload_main


def evaluate(query, input_file, eps, quant, repeat):
    data = read_input_file(input_file)
    bounds = (l, u) = (np.min(data), np.max(data))
    with tempfile.NamedTemporaryFile() as tmp:
        conn = sqlite3.connect(tmp.name)
        c = conn.cursor()
        c.execute("CREATE TABLE t (v REAL)")
        c.executemany("INSERT INTO t VALUES (?)", [(d,) for d in data])
        conn.commit()
        conn.close()

        results = []
        for i in range(repeat):
            if query == "count":
                result = QueryWithDP(tmp.name, SCHEMA_FILE, "SELECT COUNT(v) FROM t", "LaplaceMechClipping", eps, l, u).run()
            elif query == "sum":
                result = QueryWithDP(tmp.name, SCHEMA_FILE, "SELECT SUM(v) FROM t", "LaplaceMechClipping", eps, l, u).run()
            elif query == "mean":
                result = QueryWithDP(tmp.name, SCHEMA_FILE, "SELECT AVG(v) FROM t", "AverageMechClipping", eps, l, u).run()
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
