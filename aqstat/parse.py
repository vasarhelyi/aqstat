"""Parsing functions for AQData classes."""

import csv
from datetime import datetime

def parse_raw_aq_csv(filename):
    """Read raw AQ data from csv file."""
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        header = None
        data = {}
        for row in csv_reader:
            if header is None:
                header = row
                for key in header:
                    data[key] = []
            else:
                for key, value in zip(header, row):
                    try:
                        if key == "Time":
                            data[key].append(datetime.strptime(value, '%Y/%m/%d %H:%M:%S'))
                        elif value == "":
                            data[key].append(float("nan"))
                        else:
                            data[key].append(float(value))
                    except ValueError:
                        print("ERROR parsing file {}, line {}, column '{}', value '{}'".format(
                            filename, csv_reader.line_num, key, value))
                        raise
    return data
