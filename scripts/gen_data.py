"""
Generate Synthetic Datasets for the DP Benchmark
- Scale (250) and skew (5) - Size 1/10/100k
- Scale (50/500) and skew (5) - Size 10k
- Scale (250) and skew (0/50) - Size 10k
- Performance - scale (250) and skew (5) - Size 10^{1..2, 6..9}
"""

import os
import numpy as np
from scipy.stats import skewnorm


SYN_TARGETS = [
    (5, 250, 4),
    # various sizes
    (5, 250, 3), 
    (5, 250, 5),
    # various scales
    (5, 50, 4),
    (5, 500, 4),
    # various skews
    (0, 250, 4),
    (50, 250, 4),
    # performance test
    *[(5, 250, _) for _ in range(1, 3)],
    *[(5, 250, _) for _ in range(6, 10)],
]

def main(location = None):
    if location is None:
        try:
            os.makedirs("./data")
        except FileExistsError:
            pass
        location = "./data"
    for (skew, scale, log_size) in SYN_TARGETS:
        size = 10 ** log_size
        filename = f"{location}/skewnorm_skew-{skew}_scale-{scale}_size-1e{log_size}.csv"
        print(f"Generating {filename}...\t", end="")
        data = skewnorm.rvs(a=skew, loc=0, scale=scale, size=size)
        np.savetxt(filename, data, delimiter="\n")
        print(f"{os.path.getsize(filename)/1e6:.2f} MB generated.")


if __name__ == "__main__":
    main()
