from ast import arg
import sys
import os
import json
import argparse
import tempfile
import importlib
import numpy as np

from dp_benchmark.monitor import measure_func_workload, measure_command_workload
from dp_benchmark.library_workload import WORKLOAD_DIR
from dp_benchmark.library_workload.baseline import evaluate as baseline_evaluate


def evaluate_library(library, mode, query, input_file, eps, quant, repeat, python_command, external_sample_interval):
    # handle the handy query types
    if query == "quantile25":
        query = "quantile"
        quant = 0.25
    elif query == "quantile75":
        query = "quantile"
        quant = 0.75

    result = {
        "library": library,
        "mode": mode,
        "query": query,
        "input_file": input_file,
        "epsilon": eps,
        "quant": quant,
        "repeat": repeat,
        "external_sample_interval": external_sample_interval,
        "_workload_dir": WORKLOAD_DIR,
    }
    
    # run the workload, merge the result
    if mode == "plain":
        evaluate_func = importlib.import_module(f'dp_benchmark.library_workload.{library}').evaluate
        result["_dp_results"] = dp_results = evaluate_func(query, input_file, eps, quant, repeat)
    elif mode == "internal":
        evaluate_func = importlib.import_module(f'dp_benchmark.library_workload.{library}').evaluate
        dp_results, measurements = measure_func_workload(evaluate_func, {
            "query": query,
            "input_file": input_file,
            "eps": eps,
            "quant": quant,
            "repeat": repeat,
        })
        if isinstance(dp_results, Exception):
            raise(dp_results)
        result["_dp_results"] = dp_results
        result.update(measurements)
    elif mode == "external":
        with tempfile.NamedTemporaryFile() as fp:
            output_file = fp.name
            external_measurements = measure_command_workload([
                python_command, "-m", 
                f"dp_benchmark.library_workload.{library}",
                query, input_file, output_file,
                "--epsilon",  str(eps),
                *([] if quant is None else ["--quant", str(quant)]),
                "--repeat", str(repeat),
                "--force"], interval=external_sample_interval)
            with open(output_file, "r") as f:
                internal_results = json.load(f)
                dp_results = internal_results["dp_results"]
                internal_measurements = internal_results["measurements"]
        result["_dp_results"] = dp_results
        result.update(internal_measurements)
        result.update(external_measurements)
    else:
        raise ValueError(f"Unknown mode '{mode}'")

    # compare with std result from baseline (no dp)
    data_size = baseline_evaluate("count", input_file, eps=0, quant=quant, repeat=1)[0]
    truth_result = baseline_evaluate(query, input_file, eps=0, quant=quant, repeat=1)[0]
    result["_truth_result"] = truth_result
    
    # calculate the dp error
    result["dp_mre"] = mean_of_relative_err = np.mean(np.abs(np.array(dp_results) - truth_result) / np.abs(truth_result))
    result["dp_sase"] = sample_std_of_absolute_scaled_err = np.std(np.abs(np.array(dp_results) - truth_result) / data_size)

    return result


def main(unparsed_args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", "-v", action="version", version="dpbench 0.0")
    parser.add_argument("library", choices=["baseline", "diffprivlib", "pydp", "opendp", "tmlt", "chorus"])
    parser.add_argument("query", choices=["count", "sum", "mean", "var", "median", "quantile",  "quantile25", "quantile75"])
    parser.add_argument("input_file")
    parser.add_argument("output_file")
    parser.add_argument("--mode", "-m", choices=["internal", "external"], default="internal")
    parser.add_argument("--epsilon", "-e", type=float, default=1)  # default: 0.1 / 1 / 10
    parser.add_argument("--quant", "-q", type=float, default=None)
    parser.add_argument("--repeat", "-r", type=int, default=1)
    parser.add_argument("--force", "-f", action="store_true")
    parser.add_argument("--debug", "-d", action="store_true")
    parser.add_argument("--python_command", type=str, default="python3")
    parser.add_argument("--external_sample_interval", type=float, default=0.1)

    if unparsed_args is not None:
        if isinstance(unparsed_args, str):
            unparsed_args = unparsed_args.split(" ")
        args = parser.parse_args(unparsed_args)
    else:
        args = parser.parse_args()

    # set baseline epsilon to zero and prompt
    if args.library == "baseline" and args.epsilon != 0:
        print("Library is set to baseline (no dp), epsilon is forced to set to 0.", file=sys.stderr)
        args.epsilon = 0

    # handle quantile value
    if args.query != "quantile" and args.quant is not None:
        raise argparse.ArgumentError("quantile argument is only applicable to query=quantile")
    if args.query == "quantile" and args.quant is None:
        print("Query is set to quantile, quant is forced to set to 0.25.", file=sys.stderr)
        args.quant = 0.25
    if args.query == "quantile" and (args.quant < 0 or args.quant > 1):
        raise argparse.ArgumentError("quantile is only applicable to quant between 0 and 1")

    # convert to absolute path and check file existence
    args.input_file = os.path.abspath(args.input_file)
    args.output_file = os.path.abspath(args.output_file)
    if not os.path.isfile(args.input_file):
        raise FileNotFoundError(f"Input file '{args.input_file}' does not exist")        
    if os.path.isfile(args.output_file) and not args.force:
        raise FileExistsError(f"Output file '{args.output_file}' already exists, please use --force to overwrite")

    # evaluate library and write results to output file
    result = evaluate_library(args.library, args.mode, args.query, args.input_file, args.epsilon, args.quant, args.repeat, args.python_command, args.external_sample_interval)
    if not args.debug:
        keys = list(result.keys())
        for k in keys:
            if k.startswith("_"):
                del result[k]
    with open(args.output_file, "w") as f:
        json.dump(result, f, indent=2)


if __name__ == "__main__":
    main()
