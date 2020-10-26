#! /usr/bin/env python
import argparse
import json
from zipfile import ZipFile


from urllib import request, error
from pathlib import Path


class TekDownloader:
    def __init__(self):
        self.oldnum = None;
        self.newnum = None;
        pass

    def setOutDir(self, outdir):
        self.outdir = outdir

    def setOldNum(self, n):
        self.oldnum = n

    def setNewNum(self,n):
        self.newnum =n

    def run(self):
        try:
            reqHeaders = {"User-Agent": "Mozilla/5.0","Accept": "application/json", "Cache-Control": "no-cache"}
            req = request.Request(url='https://get.immuni.gov.it/v1/keys/index', headers=reqHeaders)
            response = request.urlopen(req)
            indexJson = response.read().decode("utf-8")
            index = json.loads(indexJson)
            print("Available Indexes: {0} to {1}".format(index["oldest"], index["newest"]))

            if args.index:
                exit(0)

            if self.oldnum is None:
                self.oldnum = index["oldest"]
            else:
                self.oldnum = max (self.oldnum+1, index["oldest"])

            if self.newnum is None:
                self.newnum = index["newest"]
            else:
                self.newnum = min (self.newnum, index["newest"])

            for batch in range(self.oldnum,self.newnum+1):
                print("Reading Batch {}".format(batch))
                req = request.Request(url='https://get.immuni.gov.it/v1/keys/{}'.format(batch), headers=reqHeaders)
                response = request.urlopen(req)
                outfile = Path(self.outdir, "{}.zip".format(batch));
                outf = open(outfile,"wb")
                outf.write(response.read())
                outf.close()

                print("{} bytes read".format(outfile.stat().st_size))

                outdir = Path(self.outdir, "{}".format(batch))
                outdir.mkdir()

                with ZipFile(outfile,"r") as zip:
                    zip.extractall(outdir)

                exported = Path(outdir, "export.bin")
                print("File {0} extracted to export.bin ({1} bytes)".format(outfile, exported.stat().st_size))



        except error.URLError as e:
            print("Fail: ", e.reason)
            print(e.read())



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--country", help="Country, defines the method and server to use")
    parser.add_argument("--outdir", help="where to save files")
    parser.add_argument("--old", help="Progressive id of the oldest batch. Optional. If missing, download all from the oldest available")
    parser.add_argument("--new", help="Progressive id of the newest batch. Optional. If missing, download all up to the newest available ")
    parser.add_argument("--index", default=False, action="store_true" ,help="Just pick index and exit")
    args = parser.parse_args()

    downloader = TekDownloader()
    downloader.setOutDir(args.outdir)
    if not args.old is None:
        downloader.setOldNum(int(args.old))
    if not args.new is None:
        downloader.setNewNum(int(args.new))

    downloader.run()