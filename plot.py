#!/usr/bin/env python3
from pathlib import Path

import click
import pandas


@click.command()
@click.option("--skip-rows", type=int, default=0)
@click.argument("input")
def main(input, skip_rows):
    if not input.endswith(".csv"):
        raise click.Abort(f"I expected a CSV file, but got {input}")

    df = pandas.read_csv(
        input,
        names=["time", "voltage"],
        # infer_datetime_format=True,
        skiprows=skip_rows,
        parse_dates=[0],
    )
    output_file = Path(input).stem + ".png"
    df.set_index("time").plot().figure.savefig(output_file)
    df.plot(x="time", y="voltage")


if __name__ == "__main__":
    main()
