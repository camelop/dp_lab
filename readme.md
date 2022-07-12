## How to run the experiments in the benchmark

1. Clone the repo, switch the working directory, and install the dependencies
    ```
    git clone ***
    cd dp_benchmark
    pip install -e .
    ```
2. Run the experiment with CLI
    ```sh
    dpbench <library> <operation> <input_file> <output_file> <other options>
    ```
    For example:
    ```sh
    dpbench pydp sum data/1.csv data/1.json -f -r 1000
    ```

### Generating synthetic data

```sh
# Make sure you are in the root directory of the repo
# Data will be generated in the ./data/ directory
# The procedure will generate about 28GB of data
# To avoid the risk of running out of disk space, you can comment out the performance test lines (Line26-27) in SYN_TARGETS defined in the script
python3 scripts/gen_data.py
```
