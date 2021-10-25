##
import pandas as pd
import os
import numpy as np
from matplotlib import pyplot as plt


##

data = os.path.join("Data", "data-export-72745-4631575461113875173")

df_sec = pd.read_csv(os.path.join(data, "c92c0a-SmartPlug_1-1SEC.csv"))
df_min = pd.read_csv(os.path.join(data, "c92c0a-SmartPlug_1-1MIN.csv"))


df_sec["Power"] = df_sec["SmartPlug 1_1 (kWatts)"] * 1000
df_sec["Energy"] = df_sec["Power"] * 1/(60**2)
df_sec["datetime"] = pd.to_datetime(df_sec["Time Bucket (America/New_York)"], format="%m/%d/%Y %H:%M:%S")
df_sec["ts"] = df_sec["datetime"].values.astype(np.int64) // 10 ** 9
df_sec.drop(columns=["Time Bucket (America/New_York)", "SmartPlug 1_1 (kWatts)"], inplace=True)

df_min["Power"] = df_min["SmartPlug 1_1 (kWatts)"] * 1000
df_min["Energy"] = df_min["Power"] * 1/60
df_min["datetime"] = pd.to_datetime(df_min["Time Bucket (America/New_York)"], format="%m/%d/%Y %H:%M:%S")
df_min["ts"] = df_min["datetime"].values.astype(np.int64) // 10 ** 9
df_min.drop(columns=["Time Bucket (America/New_York)", "SmartPlug 1_1 (kWatts)"], inplace=True)

df_min = df_min[df_min["datetime"] >= df_sec["datetime"].min()]

##
plt.plot(df_sec["datetime"], df_sec["Power"], label="sec")
plt.plot(df_min["datetime"], df_min["Power"], label="min")
plt.legend()
plt.ylabel("W")
plt.xlabel("Datetime")
plt.gcf().autofmt_xdate()
plt.show()

