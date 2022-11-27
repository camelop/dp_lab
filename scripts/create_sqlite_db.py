import os
import sqlite3


def convert(file_loc):
    assert file_loc.endswith(".csv")
    with open(file_loc, "r") as f:
        data = [float(_) for _ in f.read().splitlines() if _.strip()]
    if os.path.exists(file_loc.replace(".csv", ".db")):
        os.remove(file_loc.replace(".csv", ".db"))
    conn = sqlite3.connect(file_loc[:-4] + ".db")
    c = conn.cursor()
    c.execute("CREATE TABLE t (v REAL)")
    c.executemany("INSERT INTO t VALUES (?)", [(d,) for d in data])
    conn.commit()
    conn.close()


if __name__ == "__main__":
    convert("./data/1.csv")
