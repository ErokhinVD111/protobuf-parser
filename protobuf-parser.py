import sys
import os
from google.protobuf.json_format import MessageToJson, ParseDict
import Config_pb2 as Config_pb2
import json


class ProtobufParser:
    def __init__(self, ProtobufMessage):
        self.message = ProtobufMessage()

    def bin_to_message(self, file_name):
        with open(file_name, "rb") as f:
            bin_string = f.read()
        self.message.ParseFromString(bin_string)

    def save_message_as_bin(self, file_name):
        if not os.path.exists(sys.argv[2]):
            os.mkdir(sys.argv[2])
        with open("{}/{}".format(sys.argv[2], file_name), "wb") as f:
            f.write(self.message.SerializePartialToString())

    def save_message_as_json(self, file_name):
        if not os.path.exists(sys.argv[2]):
            os.mkdir(sys.argv[2])
        with open(file_name, "w") as f:
            json.dump(json.loads(MessageToJson(self.message)), f, indent=4)

    def read_json(self):
        if not os.path.exists(sys.argv[1]):
            raise FileNotFoundError("json file not found")
        with open(sys.argv[1], "r") as f:
            return json.load(f)

    def json_to_message(self, file_name=None, json_string=None):
        if json_string:
            read_json_string = json_string
        elif file_name:
            read_json_string = self.read_json()
        else:
            raise FileNotFoundError()
        ParseDict(read_json_string, self.message)


if __name__ == "__main__":
    path = sys.argv[1]
    dirs = os.listdir(path)
    protobufParser = ProtobufParser(Config_pb2.CfgMsg)
    for file in dirs:
        protobufParser.bin_to_message(path + "/" + file)
        protobufParser.save_message_as_json(sys.argv[2] + "/" + file)
