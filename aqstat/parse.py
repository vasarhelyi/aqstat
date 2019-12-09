"""Parsing functions for AQData classes."""

import csv
from datetime import datetime

def parse_raw_aq_csv(filename):
    """Read raw AQ data from csv file.

    Parameters:
        filename (path): the file to parse. Format of the file is expected to be
            the one used by the luftdaten.info project, e.g. as here:
            https://www.madavi.de/sensor/csvfiles.php?sensor=esp8266-11797099

    Return:
        data dictionary where eah key is a column header in the original .csv
        and each value is a list of the data from that specific column.

    """
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
