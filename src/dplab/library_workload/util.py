import os
import time
import json
import argparse
from functools import partial
import numpy as np

from dplab.monitor import measure_func_workload


def read_input_file(file):
    current = time.time()
    result = partial(np.loadtxt, skiprows=0)(file)
    time_used = time.time() - current
    return result, time_used


def workload_main(evaluate_func, unparsed_args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("query", choices=["count", "sum", "mean", "var", "median", "quantile"])
    parser.add_argument("input_file")
    parser.add_argument("output_file")
    parser.add_argument("--epsilon", "-e", type=float, default=1)  # default: 0.1 / 1 / 10
    parser.add_argument("--quant", "-q", type=float, default=None)
    parser.add_argument("--lb", type=float, default=None)
    parser.add_argument("--ub", type=float, default=None)
    parser.add_argument("--repeat", "-r", type=int, default=1)
    parser.add_argument("--force", "-f", action="store_true")
    if unparsed_args is not None:
        if isinstance(unparsed_args, str):
            unparsed_args = unparsed_args.split(" ")
        args = parser.parse_args(unparsed_args)
    else:
        args = parser.parse_args()
    
    # convert to absolute path and check file existence
    args.input_file = os.path.abspath(args.input_file)
    args.output_file = os.path.abspath(args.output_file)
    if not os.path.isfile(args.input_file):
        raise FileNotFoundError(f"Input file '{args.input_file}' does not exist")        
    if os.path.isfile(args.output_file) and not args.force:
        raise FileExistsError(f"Output file '{args.output_file}' already exists, please use --force to overwrite")
    (dp_results, in_func_measurement), measurements = measure_func_workload(evaluate_func, {
            "query": args.query,
            "input_file": args.input_file,
            "eps": args.epsilon,
            "quant": args.quant,
            "lb": args.lb,
            "ub": args.ub,
            "repeat": args.repeat,
    })

    # save result to output file
    result = {
        "dp_results": dp_results,
        "measurements": {**measurements, **in_func_measurement},
    }
    with open(args.output_file, "w") as f:
        json.dump(result, f)
