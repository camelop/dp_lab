import numpy as np
from pydp.algorithms import laplacian as pydp

from dplab.library_workload.util import read_input_file, workload_main


def evaluate(query, input_file, eps, quant, lb, ub, repeat):
    data = read_input_file(input_file)
    lb = np.min(data) if lb is None else lb
    ub = np.max(data) if ub is None else ub
    results = []
    for i in range(repeat):
        if query == "count":
            x = pydp.Count(epsilon=eps, dtype='float')
            result = x.quick_result(list(data))
        elif query == "sum":
            x = pydp.BoundedSum(eps, 0, lb, ub, dtype='float')
            result = x.quick_result(list(data))
        elif query == "mean":
            x = pydp.BoundedMean(eps, 0, lb, ub, dtype='float')
            result = x.quick_result(list(data))
        elif query == "var":
            x = pydp.BoundedVariance(eps, 0, lb, ub, dtype='float')
            result = x.quick_result(list(data))
        elif query == "median":
            x = pydp.Median(eps, 0, lb, ub, dtype='float')
            result = x.quick_result(list(data))
        elif query == "quantile":
            x = pydp.Percentile(eps, quant, lb, ub, dtype='float')
            result = x.quick_result(list(data))
        else:
            raise ValueError("Unknown query: {}".format(query))
        results.append(result)
    return results


if __name__ == "__main__":
    workload_main(evaluate)
