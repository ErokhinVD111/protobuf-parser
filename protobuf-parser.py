import sys
import os
from google.protobuf.json_format import MessageToJson, ParseDict
from google.protobuf.message import DecodeError
import Config_pb2 as Config_pb2
import json


class ProtobufParser:
    def __init__(self, ProtobufMessage):
        self.message = ProtobufMessage()

    def bin_to_message(self, path):
        with open(path, "rb") as f:
            bin_string = f.read()
            self.message.ParseFromString(bin_string)

    def save_message_as_bin(self, path, file_name):
        if not os.path.exists(path):
            os.mkdir(path)
        with open(path + "/" + file_name, "wb") as f:
            f.write(self.message.SerializePartialToString())

    def save_message_as_json(self, path):
        if not os.path.exists(path):
            os.mkdir(path)
        with open(path, "w") as f:
            json.dump(json.loads(MessageToJson(self.message)), f, indent=4)

    def read_json(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError("json file not found")
        with open(path, "r") as f:
            return json.load(f)

    def json_to_message(self, path=None, json_string=None):
        if json_string:
            read_json_string = json_string
        elif path:
            read_json_string = self.read_json(path)
        else:
            raise FileNotFoundError()
        ParseDict(read_json_string, self.message)


if __name__ == "__main__":
    mode = input("""
    "b2j" (binaries to json) how to use: python3 b2j [path to binaries files] [path to *.json] [out path]
    "j2b" (json to binaries) how to use: python3 j2b [path to *json] [out path]
    mode:
    """)
    if mode == "b2j":
        # path to bin files
        path = sys.argv[1]
        dirs = os.listdir(path)

        # object for parsing
        protobufParser = ProtobufParser(Config_pb2.CfgMsg)

        names_layers = []

        # jsons from bin files without "data"
        jsons_from_bins = {}

        for file in sorted(dirs):
            try:
                # get message
                protobufParser.bin_to_message(path + "/" + file)
                # get json without data
                json_without_data = json.loads(MessageToJson(protobufParser.message))["data"]
                # append to dict json whithout data
                key = list(dict(json_without_data).keys())[0]
                value = list(dict(json_without_data).values())[0]
                jsons_from_bins[key] = value
                # get names of all layers
                names_layers.append(key)
            except DecodeError:
                print("Can't decode " + file)

        # replace main_json
        protobufParser = ProtobufParser(Config_pb2.CfgMsg)
        main_json = protobufParser.read_json(sys.argv[2])
        for name_layer in names_layers:
            try:
                main_json["tedix-r-sr"]["v2x"]["messages"][name_layer] = jsons_from_bins[name_layer]
            except KeyError:
                print("key", name_layer, "not found")
        if not os.path.exists(sys.argv[3]):
            os.mkdir(sys.argv[3])
        with open(sys.argv[3] + "/main_config.json", "w") as f:
            json.dump(main_json, f, indent=4)

    elif mode == "j2b":
        protobufParser = ProtobufParser(Config_pb2.CfgMsg)
        json_string = protobufParser.read_json(sys.argv[1])
        v2x_json_string = json_string["tedix-r-sr"]["v2x"]["messages"]
        delete_keys_list = [
            "capture_cache_size",
            "CAM",
            "DENM",
            "MAP"
        ]
        for key in delete_keys_list:
            del v2x_json_string[key]
        for key, value in v2x_json_string.items():
            protobufParser.json_to_message(json_string={"data": {"{}".format(key): value}})
            protobufParser.save_message_as_bin(sys.argv[2], key)
