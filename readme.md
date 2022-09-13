# Benchmarking Differential Privacy Aggregation Operation 

This repo targets to provide a unified interface to access and evaluate the same aggregation functionalities in different open-source differential privacy (DP) libraries. With a simple CLI, one can choose the library, the aggregation function, and many other experimental parameters and apply the specified DP measurement to data stored in a `.csv` file. The repo also provides both synthetic and real-world example datasets for evaluation purposes. Evaluation results are stored in a `.json` file and metrics are provided for repeated experiments. The repo also provides a CLI tool to generate configuration groups for larger-scale comparison experiments. 

**Currently supported aggregation operations**: 
- COUNT
- SUM
- MEAN
- VAR
- MEDIAN 
- QUANTILE

**Currently supported libraries**:
- diffprivlib 0.5.2 [[Homepage](https://github.com/IBM/differential-privacy-library)] [[Example Usage](./src/dp_benchmark/library_workload/diffprivlib.py)]
- python-dp 1.1.1 [[Homepage](https://github.com/OpenMined/PyDP)] [[Example Usage](./src/dp_benchmark/library_workload/pydp.py)]
- opendp 0.5.0 [[Homepage](https://opendp.org/)] [[Example Usage](./src/dp_benchmark/library_workload/opendp.py)]
- tmlt.analytics 0.4.1 [[Homepage](https://docs.tmlt.dev/analytics/latest/index.html)] [[Example Usage](./src/dp_benchmark/library_workload/tmlt.py)]
- chorus [[Homepage](https://github.com/uvm-plaid/chorus)] (coming soon)

![dp_bench_architecture](./img/dp_bench_architecture.png)

## Installation

Clone the repo, switch the working directory, and install the dependencies
```
git clone ***
cd dp_benchmark
pip install -e .
```

To use [tmlt](https://docs.tmlt.dev/analytics/latest/installation.html)
```
export PYSPARK_PYTHON=/usr/bin/python3
sudo apt install openjdk-8-jre-headless
pip3 install -i https://d3p0voevd56kj6.cloudfront.net python-flint
pip3 install tmlt.analytics
```

## How to run experiments in the benchmark

Generate the experiment commands, this will generate an `./exp.db.json` file under the working directory (you can also use `--location` to specify a different place).

```sh
dpbench_exp plan --repeat 100 --group_num 100
```

Queue the experiments for execution
```sh
dpbench_exp launch --debug
```

## How to run dp libraries in the benchmark

Run a specific library with the CLI

```sh
dpbench_run <library> <operation> <input_file> <output_file> <other options>
```

For example:
```sh
dpbench_run pydp sum data/1.csv data/1.json -f -r 1000
```

### Generating synthetic data

```sh
# Make sure you are in the root directory of the repo
# Data will be generated in the ./data/ directory
# The procedure will generate about 28GB of data
# To avoid the risk of running out of disk space, you can comment out the performance test lines (Line26-27) in SYN_TARGETS defined in the script
python3 scripts/gen_data.py
```
