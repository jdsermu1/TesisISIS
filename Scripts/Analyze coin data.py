##

import pandas as pd
import os
from matplotlib import pyplot as plt
from pandas_profiling import ProfileReport
from scipy.signal import lfilter
from scipy.interpolate import Rbf
#import statsmodels.api as sm

##

coins = {"ethereum": {"monitor_dir": "09-11-2021 10-09-48", "reported_hashrate": 0},
         "ergo": {"monitor_dir": "11-11-2021 08-40-46", "reported_hashrate": 3.20e6},
         "raven_coin": {"monitor_dir": "10-11-2021 08-30-20", "reported_hashrate": 1.25e6},
         "ethereum_classic": {"monitor_dir": "05-11-2021 13-40-17", "reported_hashrate": 1.37e6}}

base_dir = os.path.join("", "Data")


max_hour = 5


def load_power_data(path):
    df = pd.read_csv(path)
    df["Power"] = df["SmartPlug 1_1 (kWatts)"] * 1000
    df["Energy"] = df["Power"] * 1 / (60 ** 2)
    df["ts"] = pd.to_datetime(df["Time Bucket (America/New_York)"], format="%m/%d/%Y %H:%M:%S")
    df["ts"] = df["ts"].dt.tz_localize('America/New_York')
    df.drop(columns=["Time Bucket (America/New_York)", "SmartPlug 1_1 (kWatts)"], inplace=True)
    return df


def load_monitor_data(coin_name, monitor_dir, reported_hashrate):
    df_monitor_coin = pd.read_csv(os.path.join(base_dir, coin_name, monitor_dir, "data.csv"))
    df_monitor_coin["ts"] = pd.to_datetime(df_monitor_coin["ts"], format="%m/%d/%Y %H:%M:%S")
    df_monitor_coin["ts"] = df_monitor_coin["ts"].dt.tz_localize('America/Bogota')
    df_monitor_coin["gpu_load"] = df_monitor_coin["gpu_load"] * 100
    df_monitor_coin["gpu_memory_usage"] = df_monitor_coin["gpu_memory_usage"] * 2 ** 20

    df_monitor_coin["hashrate"] = df_monitor_coin["hashrate"].fillna(0)
    df_monitor_coin["reported_hashrate"] = df_monitor_coin["gpu_load"] / 100 * reported_hashrate
    df_monitor_coin["relative_hour"] = (df_monitor_coin["ts"] - df_monitor_coin["ts"].min()).map(lambda x: x.total_seconds()/(60**2))
    df_monitor_coin = df_monitor_coin[df_monitor_coin["relative_hour"] <= max_hour]
    df_monitor_coin = df_monitor_coin.sort_values("relative_hour")
    return df_monitor_coin


def load_coin_power_data(coin_name, min_ts, max_ts):
    df = load_power_data(os.path.join(base_dir, coin_name, "data_power.csv"))
    df = df[(df["ts"] >= min_ts) & (df["ts"] <= max_ts)]
    df["relative_hour"] = (df["ts"] - min_ts.tz_convert("America/New_York")).map(lambda x: x.total_seconds()/(60**2))
    df = df[df["relative_hour"] <= max_hour]
    df = df.sort_values("relative_hour")
    return df


def load_all_data():
    for coin_name, dict_coin in coins.items():
        dict_coin["monitor"] = load_monitor_data(coin_name, dict_coin["monitor_dir"], dict_coin["reported_hashrate"])
        min_ts = dict_coin["monitor"]["ts"].min()
        max_ts = dict_coin["monitor"]["ts"].max()
        dict_coin["power"] = load_coin_power_data(coin_name, min_ts, max_ts)


load_all_data()


##

def plot_graph(data, labels, ylabel, xlabel, title, log_scale=False, labels_names=None):
    for i, label in enumerate(labels):
        plt.plot(data["relative_hour"], data[label], label=labels_names[i] if labels_names else label)
        # plt.plot(data["relative_time"].map(lambda x: x.total_seconds()/(60**2)), data[label], label=label)
        # plt.plot(data["ts"].dt.to_pydatetime(), data[label], label=label)

    if log_scale:
        plt.yscale("symlog")
    plt.legend()
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.title(title)
    plt.grid()
    plt.show()


def plot_data_per_coin(coin_name):
    df_monitor = coins[coin_name]["monitor"]
    df_power = coins[coin_name]["power"]
    # plot_graph(df_monitor, ["cpu_load", "gpu_load"], "%", "Hour", "Load vs. Time", log_scale=True)
    # plot_graph(df_monitor, ["cpu_temp", "gpu_temp"], "C", "Hour", "Temp vs. Time")
    # plot_graph(df_monitor, ["memory_usage", "gpu_memory_usage"], "B", "Hour", "Memory Usage vs. Time")
    plot_graph(df_monitor, ["hashrate", "reported_hashrate"], "H/s", "Hora", "Hashrate vs. Tiempo",
               labels_names=["Pool", "Minero"])
    # plot_graph(df_power, ["Power"], "W", "Hour", "Wattage vs. Time")


# plot_data_per_coin("raven_coin")


##


def plot_data_to_graph(ax: plt.Axes, data: pd.DataFrame, x_name,  y_name, label=None, smooth=False, **kwargs):
    if not smooth:
        ax.plot(data[x_name], data[y_name], label=label if label else y_name)
    else:
        rolled_copy = data.rolling(10, on=x_name).mean()
        ax.plot(rolled_copy[x_name], rolled_copy[y_name], label=label if label else y_name)

        # n = 50  # larger n gives smoother curves
        # b = [1.0 / n] * n  # numerator coefficients
        # a = 1  # denominator coefficient
        # new_y = lfilter(b, a, data[y_name])
        # ax.plot(new_y, data[x_name], label=label if label else y_name)

        # rbf = Rbf(data[x_name], data[y_name], function='multiquadric', smooth=1800)
        # y_rbf = rbf(data[x_name])
        # ax.plot(data[y_name], y_rbf, label=label if label else y_name)

        # y_lowess = sm.nonparametric.lowess(data[y_name], data[x_name], frac=0.05)  # 30 % lowess smoothing
        # ax.plot(y_lowess[:, 0],  y_lowess[:, 1])




def plot_all_coins_metric(ax: plt.Axes, x_name, y_name, df_name, **kwargs):
    for coin in coins.keys():
        plot_data_to_graph(ax, coins[coin][df_name], x_name, y_name, label=coin, **kwargs)


def show_metric(ax, x_name, y_name, df_name, xlabel=None, ylabel=None, title=None, scale="linear", loc="upper right",
                **kwargs):
    plot_all_coins_metric(ax, x_name, y_name, df_name, **kwargs)
    ax.legend(loc=loc)
    ax.grid()
    ax.set_yscale(scale)
    ax.set_xlabel(xlabel if xlabel else x_name)
    ax.set_ylabel(ylabel if ylabel else y_name)
    ax.set_title(title if title else f"{y_name} vs. {x_name}")

## Grafica de uso de la ram

# fig, axes = plt.subplots()
# show_metric(axes, "relative_hour", "memory_usage", "monitor", ylabel="Bytes", xlabel="Hora",
#             title="Uso de memoria RAM vs. Tiempo", loc="lower right")
# fig.show()
#
# ## Grafica de uso de la CPU
#
# fig, axes = plt.subplots()
# show_metric(axes, "relative_hour", "cpu_load", "monitor", ylabel="%", xlabel="Hora",
#             title="Carga de la CPU vs. Tiempo", smooth=True)
# fig.show()
#
# ## Grafica de temperatura de la CPU
#
# fig, axes = plt.subplots()
# show_metric(axes, "relative_hour", "cpu_temp", "monitor", ylabel="C", xlabel="Hora",
#             title="Temperatura de la CPU vs. Tiempo", smooth=True)
# fig.show()
#
# ## Grafica de frecuencia de la CPU
#
# fig, axes = plt.subplots()
# show_metric(axes, "relative_hour", "cpu_freq", "monitor", ylabel="Hz", xlabel="Hora",
#             title="Frecuencia de la CPU vs. Tiempo", smooth=True)
# fig.show()
#
# ## Grafica de uso de la GPU
#
# fig, axes = plt.subplots()
# show_metric(axes, "relative_hour", "gpu_load", "monitor", ylabel="%", xlabel="Hora",
#             title="Carga de la GPU vs. Tiempo")
# fig.show()
#
# ## Grafica de temperatura de la GPU
#
# fig, axes = plt.subplots()
# show_metric(axes, "relative_hour", "gpu_temp", "monitor", ylabel="C", xlabel="Hora",
#             title="Temperatura de la GPU vs. Tiempo")
# fig.show()
#
# ## Grafica de uso de memoria de la GPU
#
# fig, axes = plt.subplots()
# show_metric(axes, "relative_hour", "gpu_memory_usage", "monitor", ylabel="Bytes", xlabel="Hora",
#             title="Uso de memoria de la GPU vs. Tiempo")
# fig.show()
#
# ## Grafica de consumo de potencia
#
# fig, axes = plt.subplots()
# show_metric(axes, "relative_hour", "Power", "power", ylabel="W", xlabel="Hora",
#             title="Consumo de potencia vs. Tiempo")
# fig.show()

##


def stats_power_consumption():
    for coin_name, data in coins.items():
        df_monitor = data["monitor"].copy()
        df_power = data["power"].copy()
        df_monitor = df_monitor[df_monitor["gpu_load"] > 50]
        min_time_usage = df_monitor["ts"].min()
        max_time_usage = df_monitor["ts"].max()
        df_power = df_power[(df_power["ts"] >= min_time_usage) & (df_power["ts"] <= max_time_usage)]
        profile = ProfileReport(df_power, title=f"Profile Report Power {coin_name}", explorative=True)
        profile.to_file(os.path.join(base_dir, coin_name, "profile_power.html"))
        total_energy = df_power["Energy"].sum()
        consumption_time = df_power["relative_hour"].max() - df_power["relative_hour"].min()
        mean_kwh_hour_consumption = total_energy/consumption_time
        print()
        print(f"Moneda: {coin_name}, Energia: {total_energy}, Horas: {consumption_time}, Prom. Hora Wh: {mean_kwh_hour_consumption}")


# stats_power_consumption()

## Graficar consumo de potencia para estado estable


def stable_consumption(ax: plt.Axes):
    files = ["Consumo en reposo.csv", "Consumo uso regular.csv"]
    labels = ["Reposo", "En uso"]
    for i, file in enumerate(files):
        df_file = load_power_data(os.path.join(base_dir, "Consumo regular", file))
        df_file["relative_hour"] = (df_file["ts"] - df_file["ts"].min()).map(lambda x: x.total_seconds() / (60 ** 2))
        plot_data_to_graph(ax, df_file, "relative_hour", "Power", labels[i])
        # profile = ProfileReport(df_file, title=f"Profile Report Power {labels[i]}", explorative=True)
        # profile.to_file(os.path.join(base_dir, "Consumo regular", f"{labels[i]}.png"))
    ax.legend()
    ax.set_title("Potencia (uso regular) vs. Tiempo")
    ax.set_ylabel("W")
    ax.set_ylabel("Hora")


fig, axes = plt.subplots()
stable_consumption(axes)
fig.savefig(os.path.join(base_dir, "Consumo regular", "grafica.png"))


