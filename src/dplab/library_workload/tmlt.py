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

def evaluate(query, input_file, eps, quant, repeat):
    data = read_input_file(input_file)
    bounds = (np.min(data), np.max(data))

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
            tmlt_query = QueryBuilder("data").sum("_c0", low=bounds[0], high=bounds[1])
        elif query == "mean":
            tmlt_query = QueryBuilder("data").average("_c0", low=bounds[0], high=bounds[1])
        elif query == "var":
            tmlt_query = QueryBuilder("data").variance("_c0", low=bounds[0], high=bounds[1])
        elif query == "median":
            tmlt_query = QueryBuilder("data").median("_c0", low=bounds[0], high=bounds[1])
        elif query == "quantile":
            tmlt_query = QueryBuilder("data").quantile("_c0", quantile=quant, low=bounds[0], high=bounds[1])
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
