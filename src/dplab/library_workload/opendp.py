import time
import numpy as np
from opendp.transformations import make_split_dataframe, make_select_column, make_cast, make_impute_constant, make_count, make_clamp, make_bounded_sum, make_bounded_resize, make_sized_bounded_mean, make_sized_bounded_variance
# https://docs.opendp.org/en/stable/api/python/opendp.trans.html
from opendp.measurements import make_base_discrete_laplace, make_base_laplace
from opendp.mod import enable_features, binary_search_param

enable_features('contrib')
enable_features("floating-point")

from dplab.library_workload.util import read_input_file, workload_main


def evaluate(query, input_file, eps, quant, lb, ub, repeat):
    # load the data to get len, and get lb and ub if not specified
    data, pre_loading_time = read_input_file(input_file)
    lb = np.min(data) if lb is None else lb
    ub = np.max(data) if ub is None else ub
    bounds = (lb, ub)

    # opendp data processing
    nw = time.time()
    with open(input_file, "r") as f:
        data_raw = f.read()  # To be improved: note that we load the data twice
    raw_file_loading_time = time.time() - nw

    symmetric_difference = 1  # (From opendp doc) In practice, if we had a dataset where each user can influence at most k records, we would say that the symmetric distance is bounded by k, so d_in=k.
    t_read_file = (
        make_split_dataframe(',', col_names=['data']) >>
        make_select_column(key='data', TOA=str) >>
        make_cast(TIA=str, TOA=float) >>
        make_impute_constant(0.)
    )
    def get_result_after_search(make_chain):
        scale = binary_search_param(make_chain, d_in=symmetric_difference, d_out=float(eps))
        measurement = make_chain(scale)
        return measurement(data_raw)

    results = []
    for i in range(repeat):
        if query == "count":
            transformation = t_read_file >> make_count(TIA=float)
            # Unfortunately, when measuring opendp, the parsing has to be repeated.
            make_chain = lambda s: transformation >> make_base_discrete_laplace(s)
            result = get_result_after_search(make_chain)
        elif query == "sum":
            transformation = (
                t_read_file >> 
                make_clamp(bounds=bounds) >>
                make_bounded_sum(bounds=bounds)
            )
            make_chain = lambda s: transformation >> make_base_laplace(s)
            result = get_result_after_search(make_chain)
        elif query == "mean":
            transformation = (
                t_read_file >> 
                make_clamp(bounds=bounds) >>
                make_bounded_resize(size=len(data), bounds=bounds, constant=0.) >>
                make_sized_bounded_mean(size=len(data), bounds=bounds)
            )
            make_chain = lambda s: transformation >> make_base_laplace(s)
            result = get_result_after_search(make_chain)
        elif query == "var":
            transformation = (
                t_read_file >> 
                make_clamp(bounds=bounds) >>
                make_bounded_resize(size=len(data), bounds=bounds, constant=0.) >>
                make_sized_bounded_variance(size=len(data), bounds=bounds)
            )
            make_chain = lambda s: transformation >> make_base_laplace(s)
            result = get_result_after_search(make_chain)
        elif query == "median":
            raise NotImplementedError("OpenDP(0.6.1) does not support median/quantile.")
        elif query == "quantile":
            raise NotImplementedError("OpenDP(0.6.1) does not support median/quantile.")
        else:
            raise ValueError("Unknown query: {}".format(query))
        results.append(result)
    return results, {"loading_time": pre_loading_time + raw_file_loading_time, "pre_loading_time": pre_loading_time, "raw_file_loading_time": raw_file_loading_time}


if __name__ == "__main__":
    workload_main(evaluate)
