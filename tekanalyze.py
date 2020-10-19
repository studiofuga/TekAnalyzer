#! /usr/bin/env python

import sys
import argparse
import Exposure_Key_Format_pb2
from datetime import datetime


class TekAnalyze:
    def __init__(self, argv):
        parser = argparse.ArgumentParser()
        parser.add_argument("--url", help="Help from which the app will download the TEKs")
        parser.add_argument("--tekfile", help="File to analyze (disables download)")
        self.args = parser.parse_args()

    def run(self):
        if self.args.tekfile:
            self.parse_tek_file(self.args.tekfile)

    def parse_tek_file(self, filename):
        f = open(filename, "rb")
        text = f.read()

        signature = bytearray(text[0:12]).decode()
        if signature != "EK Export v1":
            print("Signature not found: {0}".format(signature))
            return 2

        tekExport = Exposure_Key_Format_pb2.TemporaryExposureKeyExport()
        tekExport.ParseFromString(text[16:])
        print("Region: {0}".format(tekExport.region))
        print("Batch Num: {0}".format(tekExport.batch_num))
        print("Batch Size: {0}".format(tekExport.batch_size))
        print("Start Timestamp: {0} {1}".format(tekExport.start_timestamp,datetime.fromtimestamp(tekExport.start_timestamp)))
        print("End Timestamp: {0} {1}".format(tekExport.end_timestamp,datetime.fromtimestamp(tekExport.end_timestamp)))
        print("Number of Keys: {0}".format(len(tekExport.keys)))

        for key in tekExport.keys:
            keydata = key.key_data
            start = datetime.fromtimestamp(key.rolling_start_interval_number * 10 * 60 )
            if  hasattr(key,"report_type" ):
                report_type = key.report_type
            else:
                report_type = "N/A"

            if  hasattr(key,"days_since_onset_of_symptoms" ):
                onset_days = key.days_since_onset_of_symptoms
            else:
                onset_days = "N/A"


            print("Key: {0} Start: {3} Risk Level: {1} Report: {2} Days: {4}".format(
                keydata,
                key.transmission_risk_level,
                report_type,
            start, onset_days))

        return 0


if __name__== "__main__":
    app = TekAnalyze(sys.argv)
    exit(app.run())

