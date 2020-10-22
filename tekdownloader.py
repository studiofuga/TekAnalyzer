#! /usr/bin/env python
import argparse
import json
from urllib import request, error


class TekDownloader:
    def __init__(self):
        pass

    def setOutDir(self, outdir):
        self.outdir = outdir

    def run(self):
        try:
            reqHeaders = {"User-Agent": "Mozilla/5.0","Accept": "application/json", "Cache-Control": "no-cache"}
            req = request.Request(url='https://get.immuni.gov.it/v1/keys/index', headers=reqHeaders)
            response = request.urlopen(req)
            indexJson = response.read().decode("utf-8")
            index = json.loads(indexJson)
            print("Available Indexes: {0} to {1}".format(index["oldest"], index["newest"]))
        except error.URLError as e:
            print("Fail: ", e.reason)
            print(e.read())



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--country", help="Country, defines the method and server to use")
    parser.add_argument("--outdir", help="where to save files")
    parser.add_argument("--old", help="Progressive id of the oldest batch. Optional. If missing, download all from the oldest available")
    parser.add_argument("--new", help="Progressive id of the newest batch. Optional. If missing, download all up to the newest available ")
    args = parser.parse_args()

    downloader = TekDownloader()
    downloader.setOutDir(args.outdir)

    downloader.run()