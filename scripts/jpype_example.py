import jpype
import jpype.imports
from jpype.types import *

jpype.startJVM("--add-opens=java.base/java.nio=ALL-UNNAMED", classpath=['./chorus-0.1.3.2-SNAPSHOT-jar-with-dependencies.jar'])

from chorus.integration import QueryWithDP
# class QueryWithLaplaceDP(dbFileLoc: String, configFileLoc: String, query: String, epsilon: Double, l: Double, u: Double)

sum_result = QueryWithDP("./data/1.db", "./data/1.schema.yaml", "SELECT SUM(v) FROM t", "LaplaceMechClipping", 1, -123.183208326988, 1127.50378682045).run()
print(f"{sum_result=}")
cnt_result = QueryWithDP("./data/1.db", "./data/1.schema.yaml", "SELECT COUNT(v) FROM t", "LaplaceMechClipping", 1, -123.183208326988, 1127.50378682045).run()
print(f"{cnt_result=}")
avg_result = QueryWithDP("./data/1.db", "./data/1.schema.yaml", "SELECT AVG(v) FROM t", "AverageMechClipping", 1, -123.183208326988, 1127.50378682045).run()
print(f"{avg_result=}")
