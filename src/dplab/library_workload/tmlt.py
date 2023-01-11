import numpy as np
from pyspark import SparkFiles
from pyspark.sql import SparkSession
from tmlt.analytics.privacy_budget import PureDPBudget
from tmlt.analytics.query_builder import QueryBuilder
from tmlt.analytics.session import Session

from dplab.library_workload.util import read_input_file, workload_main


spark = (
    SparkSession.builder
    .config("spark.driver.extraJavaOptions", "-Dio.netty.tryReflectionSetAccessible=true")
    .config("spark.executor.extraJavaOptions", "-Dio.netty.tryReflectionSetAccessible=true")
    .getOrCreate()
)

def evaluate(query, input_file, eps, quant, lb, ub, repeat):
    data = read_input_file(input_file)
    lb = np.min(data) if lb is None else lb
    ub = np.max(data) if ub is None else ub

    data_df = spark.read.csv(SparkFiles.get(input_file), header=False, inferSchema=True)

    results = []
    for i in range(repeat):
        session = Session.from_dataframe(
            privacy_budget=PureDPBudget(epsilon=eps),
            source_id="data",
            dataframe=data_df
        )
        if query == "count":
            tmlt_query = QueryBuilder("data").count()
        elif query == "sum":
            tmlt_query = QueryBuilder("data").sum("_c0", low=lb, high=ub)
        elif query == "mean":
            tmlt_query = QueryBuilder("data").average("_c0", low=lb, high=ub)
        elif query == "var":
            tmlt_query = QueryBuilder("data").variance("_c0", low=lb, high=ub)
        elif query == "median":
            tmlt_query = QueryBuilder("data").median("_c0", low=lb, high=ub)
        elif query == "quantile":
            tmlt_query = QueryBuilder("data").quantile("_c0", quantile=quant, low=lb, high=ub)
        else:
            raise ValueError("Unknown query: {}".format(query))
        result = session.evaluate(
            tmlt_query,
            privacy_budget=PureDPBudget(epsilon=eps)
        ).first()[0]
        results.append(result)
    return results


if __name__ == "__main__":
    workload_main(evaluate)
