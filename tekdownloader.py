#! /usr/bin/env python
import argparse


class TekDownloader:
    def __init__(self):
        pass

    def setMethod(self, flavour):
        pass

    def download(self, outdir):
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--country", help="Country, defines the method and server to use")
    parser.add_argument("--outdir", help="where to save files")
    args = parser.parse_args()

    downloader = TekDownloader()
    if args.country == "it":
        downloader.setMethod("immuni")
    if args.country == "uk":
        downloader.setMethod("nhs")

