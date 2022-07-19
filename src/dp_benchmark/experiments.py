import os
import sys
import datetime
import argparse
import time
import numpy as np
import scipy
import scipy.stats as st
import tqdm
from tinydb import TinyDB, Query

from dp_benchmark.main import evaluate_library

#% Datasets

SYN_DATASETS = [
    "skewnorm_skew-5_scale-250_size-1e4.csv",
    # various sizes
    "skewnorm_skew-5_scale-250_size-1e3.csv",
    "skewnorm_skew-5_scale-250_size-1e5.csv",
    # various scales
    "skewnorm_skew-5_scale-50_size-1e4.csv",
    "skewnorm_skew-5_scale-500_size-1e4.csv",
    # various skews
    "skewnorm_skew-0_scale-250_size-1e4.csv",
    "skewnorm_skew-50_scale-250_size-1e4.csv",
]

REAL_DATASETS = [
    "US_census_age.csv",  # US census, Age
    "math_students_absences.csv",  # Portuguese education, Absences
    "Restaurant_money_spent.csv",  # Google, Money
    "Outliers_restaurant_money_spent.csv",  # Google (outliers), Money
]

ACCURACY_DATASETS = [
    *SYN_DATASETS,
    *REAL_DATASETS,
]

PERFORMANCE_DATASETS = [
    # performance test
    *[f"skewnorm_skew-5_scale-250_size-1e{_}.csv" for _ in range(1, 10)],
    # we do not need test performance for real datasets for now
]

#% Query types

QUERY_TYPES = [
    "count", 
    "sum", 
    "mean", 
    "var", 
    "median", 
    "quantile25",
    "quantile75",
]

#% libraries

LIBRARIES = [
    "diffprivlib", 
    "opendp", 
    "pydp", 
    "openmind_pydp",
]

#% epsilon

EPSILONS = [10**_ for _ in range(-2, 2)]


def main(unparsed_args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", "-v", action="version", version="dpbench 0.0")
    parser.add_argument("operation", choices=["plan", "launch"])
    parser.add_argument("--location", "-l", type=str)
    parser.add_argument("--dataset_folder", "-d", type=str)
    parser.add_argument("--repeat", "-r", type=int, default=100)
    parser.add_argument("--group_num", "-g", type=int, default=1)
    parser.add_argument("--debug", action="store_true")

    if unparsed_args is not None:
        if isinstance(unparsed_args, str):
            unparsed_args = unparsed_args.split(" ")
        args = parser.parse_args(unparsed_args)
    else:
        args = parser.parse_args()

    # further parse the arguments
    if args.location is None:
        args.location = "./exp.db.json"
    args.location = os.path.abspath(args.location)
    if args.dataset_folder is None:
        args.dataset_folder = "./data"
    assert os.path.exists(args.dataset_folder)
    args.dataset_folder = os.path.abspath(args.dataset_folder)

    if args.operation == "plan":
        if os.path.exists(args.location):
            assert input("The database already exists. Do you want to overwrite it? (y/n)").strip().lower() == "y"
            os.remove(args.location)
        db = TinyDB(args.location)
        # write an experiment execution plan to tinydb
        plans = []
        for (experiment_type, dataset) in [
            *[("A", d) for d in ACCURACY_DATASETS],
            *[("P", d) for d in PERFORMANCE_DATASETS],
        ]:
            for query_type in QUERY_TYPES:
                for library in LIBRARIES:
                    for epsilon in EPSILONS:
                        exp_name = f"{experiment_type}__{dataset}__{query_type}__{library}__{epsilon:.0e}"
                        input_file = os.path.join(args.dataset_folder, dataset)
                        output_file = os.path.join(args.location, f"{exp_name}.i.json")
                        experiment_timestamp = datetime.datetime.now().isoformat()
                        plan = {
                            "experiment_type": experiment_type,
                            "experiment_timestamp": experiment_timestamp,
                            "dataset": dataset,
                            "evaluate_param": {
                                "library": library,
                                "mode": "external" if experiment_type == "P" else "plain",
                                "query": query_type,
                                "input_file": input_file,
                                "eps": epsilon,
                                "repeat": args.repeat,
                                "quant": None,
                                "python_command": "python3",
                                "external_sample_interval": 0.01,
                            },
                            "group_num": args.group_num,
                            "equivalent_cmd": f"dpbench_run {library} {query_type} {input_file} {output_file} -e {epsilon} -r {args.repeat} --external_sample_interval 0.01",
                            "result": None,
                        }
                        plans.append(plan)
        db.insert_multiple(plans)
    elif args.operation == "launch":
        db = TinyDB(args.location)
        Q = Query()
        exps = db.search(Q.result == None)
        print(f"Exp group to run: {len(exps)}/{len(db)}", file=sys.stderr)
        for exp in tqdm.tqdm(exps):
            if args.debug:
                print(f"Running experiment {exp['experiment_type']} {exp['dataset']} {exp['evaluate_param']['library']} {exp['evaluate_param']['query']} {exp['evaluate_param']['eps']}", file=sys.stderr)
            result = {}
            try:
                r_dp_mres = []
                r_dp_sases = []
                for _ in range(exp["group_num"]):
                    r = evaluate_library(**exp["evaluate_param"])
                    r_dp_mres.append(r["dp_mre"])
                    r_dp_sases.append(r["dp_sase"])
                result["dp_mre"] = r_dp_mres
                result["dp_sase"] = r_dp_sases
                # calculate 0.99 mean confidence interval
                def calculate_stat(data):
                    l, h = st.t.interval(alpha=0.99, df=len(data)-1, loc=np.mean(data), scale=st.sem(data)) 
                    return (f"{(l+h)/2:.2} ±{(h-l)/2:.2}", (l+h)/2, l, h)
                result["dp_mre_ci"] = calculate_stat(r_dp_mres)
                result["dp_sase_ci"] = calculate_stat(r_dp_sases)
            except Exception as e:
                result["error"] = str(e)
            if args.debug:
                print(result, file=sys.stderr)
                time.sleep(3)
            db.update({"result": result}, Q.experiment_timestamp == exp["experiment_timestamp"])
    else:
        raise ValueError(f"Unknown operation: {args.operation}")
