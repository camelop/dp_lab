# Benchmarking Differential Privacy Aggregation Operation 

This repo targets to provide a unified interface to access and evaluate same aggregation functionalities in different open-source differential privacy (dp) libraries. With a simple CLI, one can choose the library, the aggregation function as well as many other experimental parameters, and apply the specified dp measurement to data stored in a `.csv` file. Evaluation results are stored in a `.json` file and metrics are provided for repeated experiments. The repo also provides a CLI tool to generate configuration groups for larger-scale comparison experiments. 

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
