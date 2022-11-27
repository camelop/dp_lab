import numpy as np
from opendp.trans import make_split_dataframe, make_select_column, make_cast, make_impute_constant, make_count, make_clamp, make_bounded_sum, make_bounded_resize, make_sized_bounded_mean, make_sized_bounded_variance
# https://docs.opendp.org/en/stable/api/python/opendp.trans.html
from opendp.meas import make_base_discrete_laplace, make_base_laplace
from opendp.mod import enable_features, binary_search_param

enable_features('contrib')
enable_features("floating-point")

from dplab.library_workload.util import read_input_file, workload_main


def evaluate(query, input_file, eps, quant, repeat):
    data = read_input_file(input_file)
    bounds = (np.min(data), np.max(data))

    # opendp data processing
    with open(input_file, "r") as f:
        data_raw = f.read()  # To be improved: note that we load the data twice
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
            raise NotImplementedError("OpenDP(0.5.0) does not support median/quantile.")
        elif query == "quantile":
            raise NotImplementedError("OpenDP(0.5.0) does not support median/quantile.")
        else:
            raise ValueError("Unknown query: {}".format(query))
        results.append(result)
    return results


if __name__ == "__main__":
    workload_main(evaluate)
