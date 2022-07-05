from setuptools import setup, find_packages


setup(
    name = "dp_benchmark",
    version = "0.0.1",
    author = "littleRound",
    packages=find_packages('src', exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    package_dir={'': 'src'},
    install_requires=[
        "psutil",
        "numpy",
        "diffprivlib==0.5.2",
        "python-dp==1.1.1",
    ],
    entry_points={
        'console_scripts': [
            'dpbench = dp_benchmark.main:main',
            # 'dpbench_gen',
            # 'dpbench_plot',
        ],
    },
)
