##
import numpy as np
import pandas as pd
import psutil
import GPUtil
import json
import os
import datetime
import sys
import time
import requests
import threading

##

mining_coin = "ergo"
timestamp = datetime.datetime.now().strftime("%d-%m-%Y %H-%M-%S")
base_dir = os.path.join("..")
data_dir = os.path.join(base_dir, "Data", mining_coin, timestamp)
wallet = json.load(open(os.path.join(base_dir, "Utils", "wallet.json")))
urls = json.load(open(os.path.join(base_dir, "Utils", "ethermine_url.json")))
timedelta = 10
max_length = 100
os.makedirs(data_dir)
assert timedelta > 9

##


class CSVWriter(threading.Thread):
    def __init__(self, cond):
        super().__init__()
        self.stop = False
        self.write_column_names = True
        self.dataframe = None
        self.condition: threading.Condition = cond


    def run(self):
        while not self.stop:
            self.condition.acquire()
            self.condition.wait()
            self.condition.release()
            if self.write_column_names and self.dataframe is not None:
                self.dataframe.to_csv(os.path.join(data_dir, "data.csv"), index=False, header=self.write_column_names)
                self.write_column_names = False
            elif self.dataframe is not None:
                self.dataframe.to_csv(os.path.join(data_dir, "data.csv"), index=False, mode="a",
                                      header=self.write_column_names)


##



def retrieve_psutil_data(data_dict:dict):
    data_dict["cpu_load"] = round(psutil.cpu_percent(), 2)
    data_dict["cpu_freq"] = round(psutil.cpu_freq().current, 2)
    data_dict["memory_usage"] = psutil.virtual_memory().used
    data_dict["cpu_temp"] = psutil.sensors_temperatures()["coretemp"][0].current



def retrieve_gputil_data(data_dict:dict):
    gpu = GPUtil.getGPUs()[0]
    data_dict["gpu_memory_usage"] = gpu.memoryUsed
    data_dict["gpu_load"] = gpu.load
    data_dict["gpu_temp"] = gpu.temperature


def retrieve_miner_data(data_dict:dict):
    req = requests.get(f"{urls[mining_coin]}/miner/{wallet[mining_coin]}/currentStats")
    data = req.json() if req.status_code == 200 else {}
    data = data["data"] if not isinstance(data["data"], str) else {}
    data_dict["hashrate"] = round(data.get("currentHashrate", np.nan), 2) if data.get("currentHashrate", np.nan) else np.nan
    data_dict["unpaid"] = data.get("unpaid", np.nan)



if __name__ == '__main__':
    run = True
    count = 0
    df = pd.DataFrame({})
    condition = threading.Condition()
    cvs_writer = CSVWriter(condition)
    cvs_writer.start()
    while run:
        try:
            data_dict = {"ts": datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")}
            retrieve_psutil_data(data_dict)
            retrieve_gputil_data(data_dict)
            retrieve_miner_data(data_dict)
            df = pd.concat([df, pd.DataFrame(data_dict, index=[0])], ignore_index=True)
            count += 1
            print(data_dict)
            if count == max_length:
                count = 0
                cvs_writer.dataframe = df
                condition.acquire()
                condition.notify()
                condition.release()
                df = pd.DataFrame([])
            time.sleep(timedelta)

        except KeyboardInterrupt:
            cvs_writer.stop = True
            condition.acquire()
            condition.notify()
            condition.release()
            print("Monitor Interrupted")
            sys.exit()










