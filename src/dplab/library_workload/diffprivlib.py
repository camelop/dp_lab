import numpy as np
import diffprivlib.tools as dplt

from dplab.library_workload.util import read_input_file, workload_main


def evaluate(query, input_file, eps, quant, lb, ub, repeat):
    data, pre_loading_time = read_input_file(input_file)
    lb = np.min(data) if lb is None else lb
    ub = np.max(data) if ub is None else ub
    bounds = (lb, ub)
    results = []
    for i in range(repeat):
        if query == "count":
            result = dplt.count_nonzero(np.ones_like(data), epsilon=eps)  # see: https://diffprivlib.readthedocs.io/en/latest/modules/tools.html#diffprivlib.tools.count_nonzero
        elif query == "sum":
            result = dplt.sum(data, epsilon=eps, bounds=bounds)
        elif query == "mean":
            result = dplt.mean(data, epsilon=eps, bounds=bounds)
        elif query == "var":
            result = dplt.var(data, epsilon=eps, bounds=bounds)
        elif query == "median":
            result = dplt.median(data, epsilon=eps, bounds=bounds)
        elif query == "quantile":
            result = dplt.quantile(data, quant=quant, epsilon=eps, bounds=bounds)
        else:
            raise ValueError("Unknown query: {}".format(query))
        results.append(result)
    return results, {"loading_time": pre_loading_time, "_pre_loading_time": pre_loading_time}


if __name__ == "__main__":
    workload_main(evaluate)
