## Installation

Clone the repo, switch the working directory, and install the dependencies
```
git clone ***
cd dp_benchmark
pip install -e .
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
