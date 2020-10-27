import Exposure_Key_Format_pb2
import sys


class TekParser:
    """A parser for Tek Export files
    """
    def __init__(self):
        pass

    def parse(self, filename):
        """Parses the file and returns the imported tek batch and keys
        :arg filename The complete path of the file to read
        :return The parsed structure, as explained in the protobuf file.
        """
        f = open(filename, "rb")
        text = f.read()

        signature = bytearray(text[0:12]).decode()
        if signature != "EK Export v1":
            print("Signature not found: {0}".format(signature))
            return 2

        tekExport = Exposure_Key_Format_pb2.TemporaryExposureKeyExport()
        tekExport.ParseFromString(text[16:])

        return tekExport

