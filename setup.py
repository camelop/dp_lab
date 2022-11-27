import sys
from setuptools import setup, find_packages

VERSIONFILE="./src/dplab/_version.py"
def get_version():
    try:
        version = open(VERSIONFILE, "rt").read().strip().split()[-1].replace('"', '')
    except:
        version = "unknown"
    return version

def get_readme():
    with open("readme.md", "r") as fh:
        return fh.read()

setup(
    name = "dplab",
    version = get_version(),
    description="DPLab: Benchmarking Differential Privacy Aggregation Operations",
    long_description=get_readme(),
    long_description_content_type="text/markdown",
    author = "littleRound",
    author_email = "xiaoyuanliu@berkeley.edu",
    packages = find_packages('src', exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    package_dir = {'': 'src'},
    install_requires = [
        "psutil",
        "numpy",
        "tinydb",
        "tqdm",
        "scipy",
        "jpype1",
        "diffprivlib==0.5.2",
        "python-dp==1.1.1",
        "opendp==0.5.0",
    ],
    entry_points = {
        'console_scripts': [
            'dplab_run = dplab.main:main',
            'dplab_exp = dplab.experiments:main',
        ],
    },
)
