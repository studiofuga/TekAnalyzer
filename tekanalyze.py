#! /usr/bin/env python
import sqlite3
import sys
import argparse
import Exposure_Key_Format_pb2
from pathlib import Path
from datetime import datetime
import binascii


class TekAnalyze:
    def __init__(self, argv):
        parser = argparse.ArgumentParser()
        parser.add_argument("--tekfile", help="File to analyze (disables download)")
        parser.add_argument("--db", help="Export keys to sqlite3 database")
        parser.add_argument("--batch", help="Number of the imported batch")
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
        print("Chunk/Batch number: {0}".format(self.args.batch))
        print("Batch Num: {0}".format(tekExport.batch_num))
        print("Batch Size: {0}".format(tekExport.batch_size))
        print("Start Timestamp: {0} {1}".format(tekExport.start_timestamp,datetime.fromtimestamp(tekExport.start_timestamp)))
        print("End Timestamp: {0} {1}".format(tekExport.end_timestamp,datetime.fromtimestamp(tekExport.end_timestamp)))
        print("Number of Keys: {0}".format(len(tekExport.keys)))

        if self.args.db:
            if self.args.batch is None:
                print("No batch id provided. Use --batch to specify one.")
                exit(2)

            newfile = not Path(self.args.db).is_file()
            self.db = sqlite3.connect(self.args.db)
            if newfile:
                with open("tekanalyzer.schema", mode="r") as file:
                    ddl = file.read()
                self.db.executescript(ddl)

            packid = self._import_batch(tekExport)

        for key in tekExport.keys:
            keydata = binascii.hexlify(key.key_data)
            startts = datetime.fromtimestamp(key.rolling_start_interval_number * 10 * 60 )
            endts = datetime.fromtimestamp((key.rolling_start_interval_number + key.rolling_period)* 10 * 60 )
            if  hasattr(key,"report_type" ):
                report_type = key.report_type
            else:
                report_type = None

            if  hasattr(key,"days_since_onset_of_symptoms" ):
                onset_days = key.days_since_onset_of_symptoms
            else:
                onset_days = None

            if self.db:
                self._import_key(tekExport, endts, key, keydata, onset_days, packid, report_type, startts)

        if self.db:
            self.db.commit()

        return 0

    def _import_key(self, tekExport, endts, key, keydata, onset_days, packid, report_type, startts):
        curs = self.db.cursor()
        sql = "INSERT OR REPLACE INTO keys(key, country, batch, start_rp, end_rp, start_timestamp, end_timestamp, report_type, days) " \
              "VALUES (?,?,?,?,?,?,?,?,?)"
        curs.execute(sql, (keydata, tekExport.region, packid, key.rolling_start_interval_number, key.rolling_period,
                           startts, endts, report_type, onset_days))

    def _import_batch(self, tekExport):
        curs = self.db.cursor()
        sql = "INSERT INTO batches(country, batchid, batchnum, batchsize, from_timestamp, to_timestamp, from_unix_timestamp, to_unix_timestamp) VALUES(?,?,?,?,?, ?,?,?)"
        curs.execute(sql, (tekExport.region, self.args.batch, tekExport.batch_num, tekExport.batch_size,
                            datetime.fromtimestamp(tekExport.start_timestamp),
                            datetime.fromtimestamp(tekExport.end_timestamp),
                           tekExport.start_timestamp, tekExport.end_timestamp))
        packid = curs.lastrowid
        self.db.commit()
        return packid


if __name__== "__main__":
    app = TekAnalyze(sys.argv)
    exit(app.run())

