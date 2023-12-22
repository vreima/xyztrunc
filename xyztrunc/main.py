import argparse

import pandas as pd
from pyproj import Transformer


def import_xyz(filepath: str) -> pd.DataFrame:
    return pd.read_csv(
        filepath, sep=" ", header=None, names=["x", "y", "z"], index_col=False
    )


def convert(data: pd.DataFrame, input_epsg: int, output_epsg: int) -> pd.DataFrame:
    trans = Transformer.from_crs(input_epsg, output_epsg, always_xy=True)

    x, y = trans.transform(data.x, data.y)

    data.x = x
    data.y = y

    return data


def trunc(data: pd.DataFrame, origin: tuple) -> pd.DataFrame:
    return data - origin


def crop(data: pd.DataFrame, x1, y1, x2, y2) -> pd.DataFrame:
    xmask = (x1 <= data.x) & (data.x <= x2)
    ymask = (y1 <= data.y) & (data.y <= y2)

    print(xmask.sum())

    print(ymask.sum())
    print((xmask & ymask).sum())
    return data[xmask & ymask]


def save_csv(data: pd.DataFrame, filepath: str) -> None:
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
        "-f",
        "--inputcrs",
        help="EPSG code for the input CRS projection.",
        type=int,
        default=None,
    )
    parser.add_argument(
        "-t",
        "--outputcrs",
        help="EPSG code for the output CRS projection.",
        type=int,
        default=None,
    )
    parser.add_argument(
        "--origin",
        type=float,
        nargs=3,
        help="Coordinates for the new origin. Accepts three float values.",
    )
    parser.add_argument("--crop", type=float, nargs=4)
    parser.add_argument("-v", "--verbose", default=False, action="store_true")
    args = parser.parse_args()

    data = import_xyz(args.filename)

    if args.verbose:
        print(f"Read {data.shape[0]} lines from {args.filename}.")
        print(
            f"Extends: {data.iloc[:,0].max() - data.iloc[:,0].min():.2f} x {data.iloc[:,1].max() - data.iloc[:,1].min():.2f} meters."
        )
        print(
            f"Height ranges from {data.iloc[:,2].min()} to {data.iloc[:,2].max()} meters."
        )

    if args.inputcrs and args.outputcrs:
        if args.verbose:
            print(
                f"Converting coordinates from EPSG:{args.inputcrs} to EPSG:{args.outputcrs}... ",
                end="",
            )
        data = convert(data, args.inputcrs, args.outputcrs)

        if args.verbose:
            print(f"Done.")

    if args.crop:
        x1, y1, x2, y2 = args.crop
        if args.verbose:
            print(
                f"Crop extends: {data.iloc[:,0].max() - data.iloc[:,0].min():.2f} x {data.iloc[:,1].max() - data.iloc[:,1].min():.2f} meters."
            )
        data = crop(data, x1, y1, x2, y2)

    save_csv(trunc(data, args.origin), args.output)
