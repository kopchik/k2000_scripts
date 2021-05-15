#!/usr/bin/env python3


import atexit
import csv
import os
import sys
import time
from datetime import datetime

import click
import serial

ser = serial.Serial(
    port="/dev/ttyUSB0",
    baudrate=19200,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    xonxoff=1,
    timeout=5,
)


def query(query, echo=True, response=True, to_float=False):
    if echo:
        print(f"query: {query}")
    raw_query = bytes(query + "\r\n", "utf8")
    ser.write(raw_query)
    # time.sleep(0.5)
    if response:
        raw_resp = ser.readline().strip()
        resp = raw_resp.decode()
        if echo:
            print(f"response: {resp}")
        if to_float:
            resp = float(resp)
        return resp


def init():
    data = query("*IDN?\r\n")
    assert "KEITHLEY" in data, "IDN failed"
    query(":CONF:VOLT:DC", response=False)
    query(":SENS:VOLT:NPLC 10", response=False)
    query(":CONF?")
    query(":DISP:ENAB 0", response=False)
    atexit.register(lambda: query(":DISP:ENAB 1", response=False))


def read_data(echo=False):
    data = query(":READ?", to_float=True)
    if echo:
        print(f"{data:.6f} {datetime.now()}")
    return data


def wait_til_next_tick(step=1, extra=-0.0005):
    now = time.time()
    prev_tick = int(now) // step * step
    next_tick = prev_tick + step
    to_wait = next_tick - now + extra
    # print(f"now is {now}")
    assert to_wait <= step, f"I should not wait {to_wait}"
    # print(f"I need to sleep {to_wait:.3f}")
    if to_wait > 0:
        time.sleep(to_wait)
    print(datetime.now())


@click.command()
@click.option("-p", "--period", type=int, default=5)
@click.argument("output", type=click.Path(exists=False, file_okay=True))
def main(output, period):
    if os.path.exists(output):
        print(f'output file "{output}" already exists!', file=sys.stderr)
        raise click.Abort()

    init()

    with open(output, "wt", newline="\n") as f:
        writer = csv.writer(f)
        while True:
            wait_til_next_tick(period)
            ts = datetime.now()
            data = read_data()
            writer.writerow([ts, data])
            f.flush()
            print(f"{data:2.6f}   {ts}")


if __name__ == "__main__":
    main()
