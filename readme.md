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
