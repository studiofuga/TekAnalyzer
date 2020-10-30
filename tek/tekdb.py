import sqlite3
import binascii
import os
from pathlib import Path
from datetime import datetime
from Exposure_Key_Format_pb2 import TemporaryExposureKeyExport, TemporaryExposureKey


class TekDatabase:
    def __init__(self, database):
        self.dbpath = database
        self.db = sqlite3.connect(database)

    def create(self):
        schema = Path(os.path.dirname(__file__), "tekanalyzer.schema")
        print("Schema: {}".format(schema))
        with open(schema, mode="r") as file:
            ddl = file.read()
        self.db.executescript(ddl)

    def importBatch(self, batchnum: int, batch: TemporaryExposureKeyExport) -> int:
        curs = self.db.cursor()
        sql = "INSERT INTO batches(country, batchid, batchnum, batchsize, from_timestamp, to_timestamp, from_unix_timestamp, to_unix_timestamp) VALUES(?,?,?,?,?, ?,?,?)"
        curs.execute(sql, (batch.region, batchnum, batch.batch_num, batch.batch_size,
                            datetime.fromtimestamp(batch.start_timestamp),
                            datetime.fromtimestamp(batch.end_timestamp),
                           batch.start_timestamp, batch.end_timestamp))
        packid = curs.lastrowid
        self.db.commit()
        return packid

    def importKey(self, key: TemporaryExposureKey, batch: TemporaryExposureKeyExport, batchId: int):
        keydata = binascii.hexlify(key.key_data)
        startts = datetime.fromtimestamp(key.rolling_start_interval_number * 10 * 60)
        endts = datetime.fromtimestamp((key.rolling_start_interval_number + key.rolling_period) * 10 * 60)
        if hasattr(key, "report_type"):
            report_type = key.report_type
        else:
            report_type = None

        if hasattr(key, "days_since_onset_of_symptoms"):
            onset_days = key.days_since_onset_of_symptoms
        else:
            onset_days = None

        if self.db:
            curs = self.db.cursor()
            sql = "INSERT OR REPLACE INTO keys(key, country, batch, start_rp, end_rp, start_timestamp, end_timestamp, risk_level, report_type, days) " \
                  "VALUES (?,?,?,?,?,?,?,?,?,?)"
            curs.execute(sql, (keydata, batch.region, batchId, key.rolling_start_interval_number, key.rolling_period,
                               startts, endts, key.transmission_risk_level,
                               report_type, onset_days))

    def getImportedBatches(self, country: str) -> set:
        sql = "SELECT batchid FROM main.batches WHERE country=?"
        cur = self.db.cursor()
        cur.execute(sql, (country,))
        allrecords = cur.fetchall()

        batches = {f[0] for f in allrecords}
        return batches

    def commit(self):
        self.db.commit()
