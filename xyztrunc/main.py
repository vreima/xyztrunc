import argparse

import pandas as pd


def import_xyz(filepath: str) -> pd.DataFrame:
    return pd.read_csv(filepath, sep=" ")


def trunc(data: pd.DataFrame, origin: tuple):
    return data - origin


def save_csv(data: pd.DataFrame, filepath: str):
    print(data)
    data.to_csv(filepath, header=False, index=False, lineterminator="\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="xyztrunc", description="Truncate xyz coordinates."
    )
    parser.add_argument("filename", type=argparse.FileType("r"))
    parser.add_argument(
        "-o", "--output", default="output.csv", type=argparse.FileType("w")
    )
    parser.add_argument(
        "-t",
        "--origin",
        type=float,
        nargs=3,
        help="Coordinates for the new origin. Accepts three float values.",
    )
    args = parser.parse_args()

    save_csv(trunc(import_xyz(args.filename), args.origin), args.output)
