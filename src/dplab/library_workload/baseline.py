import numpy as np

from dplab.library_workload.util import read_input_file, workload_main


def evaluate(query, input_file, eps, quant, lb, ub, repeat):
    data = read_input_file(input_file)
    results = []
    for i in range(repeat):
        if query == "count":
            result = np.shape(data)[0]
        elif query == "sum":
            result = np.sum(data)
        elif query == "mean":
            result = np.mean(data)
        elif query == "var":
            result = np.var(data)
        elif query == "median":
            result = np.median(data)
        elif query == "quantile":
            result = np.quantile(data, quant)
        else:
            raise ValueError("Unknown query: {}".format(query))
        results.append(result)
    return results


if __name__ == "__main__":
    workload_main(evaluate)
