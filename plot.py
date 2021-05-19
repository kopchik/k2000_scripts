#!/usr/bin/env python3
from pathlib import Path

import click
import pandas
import matplotlib.dates as mdates


@click.command()
@click.option("--skip-rows", type=int, default=0)
@click.option("--skip-footer", type=int, default=0)
@click.option("-a", "--annotate", type=str, multiple=True)
@click.option("-y", "--ylim", type=float, nargs=2)
@click.argument("input")
def main(input, skip_rows, skip_footer, annotate, ylim):
    if not input.endswith(".csv"):
        raise click.Abort(f"I expected a CSV file, but got {input}")

    df = pandas.read_csv(
        input,
        names=["time", "voltage"],
        # infer_datetime_format=True,
        skiprows=skip_rows,
        skipfooter=skip_footer,
        parse_dates=[0],
    )
    # df = df[df.voltage > 2.3][ df.voltage < 2.5001]
    output_file = Path(input).stem + ".png"
    plt = df.set_index("time").plot(
        figsize=(20, 10),
        x_compat=True)
    # plt.xaxis.set_major_locator(mdates.MinuteLocator(interval=10))

    if ylim:
        plt.axes.set_ylim(ylim)

    for a in annotate:
        ts, text = a.split("|")
        for i, row in df.iterrows():
            raw_x = str(row[0])
            if ts in raw_x:
                plt.annotate(text,
                             xy=(row[0], row[1]),
                             xycoords='data',
                             arrowprops=dict(facecolor='black', shrink=1),
                             )
                break

    plt.figure.savefig(output_file)


if __name__ == "__main__":
    main()
