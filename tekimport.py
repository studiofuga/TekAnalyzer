#! /usr/bin/env python
import sqlite3
import sys
import argparse
from datetime import datetime
from pathlib import Path
import binascii
from tek import tekparser, tekdb


class TekImporter:
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
        parser = tekparser.TekParser()
        tekExport = parser.parse(filename)

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
            self.db = tekdb.TekDatabase(self.args.db)
            if newfile:
                print("Create db: {0}".format(self.args.db))
                self.db.create()

            batchid = self.db.importBatch(self.args.batch, tekExport)

        for key in tekExport.keys:
            if self.db:
                self.db.importKey(key, tekExport, batchid)

        if self.db:
            self.db.commit()

        return 0

if __name__== "__main__":
    app = TekImporter(sys.argv)
    exit(app.run())

