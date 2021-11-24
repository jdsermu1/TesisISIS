##
import os
import requests
import json
import time


base_dir = os.path.join("..", "Data")
stats_file = os.path.join(base_dir, "stats.json")
miner_stats_url = "https://api.minerstat.com/v2/coins"
crypto_currencies = ["RVN", "ETH", "ETC", "ERG", "BTC"]
expiration_time = 60

miner_stats = {
    "RVN" : {
        "hashrate": 1.25e6,  # HashRate in H/s
        "pool_fee": 0.01,  # Number between 0-1
        "power_consumption": 0.03861,  # Number in KW of miner Consumption
        "power_price": 0.1  # Power consumption in USD/KW
    },
    "ETH" : {
        "hashrate": 0,  # HashRate in H/s
        "pool_fee": 0.01,  # Number between 0-1
        "power_consumption":  0.03147,  # Number in KW of miner Consumption
        "power_price": 0.1  # Power consumption in USD/KW
    },
    "ETC" : {
        "hashrate": 1.37e6,  # HashRate in H/s
        "pool_fee": 0.01, # Number between 0-1
        "power_consumption":  0.02408,  # Number in KW of miner Consumption
        "power_price": 0.1  # Power consumption in USD/KW
    },
    "ERG" : {
        "hashrate": 3.2e6,  # HashRate in H/s
        "pool_fee": 0.01, # Number between 0-1
        "power_consumption":  0.02759,  # Number in KW of miner Consumption
        "power_price": 0.1  # Power consumption in USD/KW
    }

}


def save_stats(stats):
    with open(stats_file, "w") as outfile:
        json.dump(stats, outfile)


def read_stats():
    with open(stats_file) as json_file:
        data = json.load(json_file)
        return data


def get_stats():
    return requests.get(miner_stats_url, params={"list": ",".join(crypto_currencies)}).json()


def load_stats():
    if os.path.exists(stats_file):
        saved_stats = read_stats()
        if time.time()-saved_stats.get("timestamp", 0) > expiration_time:
            stats = {"timestamp": time.time(), "data": get_stats()}
            save_stats(stats)
            return stats
        else:
            return saved_stats
    else:
        stats = {"timestamp": time.time(), "data": get_stats()}
        save_stats(stats)
        return stats

##


def calculate_mean_time_block(coin_name, difficulty, nethash):
    return difficulty * (2**32 if coin_name in ["BTC", "RVN"] else 1) / nethash


def calculate_time_reward_coin(coin_stats, miner_coin_stats, period):
    hashrate_share = miner_coin_stats["hashrate"] / (miner_coin_stats["hashrate"] + coin_stats["network_hashrate"])
    daily_blocks = 24*60**2 / calculate_mean_time_block(coin_stats["coin"],
                                                        coin_stats["difficulty"], coin_stats["network_hashrate"])
    daily_currency = daily_blocks * coin_stats["reward_block"]
    expected_currency = daily_currency * hashrate_share * (1 - miner_coin_stats["pool_fee"])
    revenue = expected_currency * coin_stats["price"]
    powerExpenses = period * miner_coin_stats["power_consumption"] * miner_coin_stats["power_price"]
    income = revenue - powerExpenses
    return income



def calculate_time_reward_all_coins(coins_stats, miner, period=24):
    for coin_data in coins_stats["data"]:
        if not miner.get(coin_data["coin"]):
            print(f"No miner data for {coin_data['coin']}")
        else:
            income = calculate_time_reward_coin(coin_data, miner[coin_data["coin"]], period)
            print(f"Income for {coin_data['coin']}: {income} USD")


current_stats = load_stats()
calculate_time_reward_all_coins(current_stats, miner_stats)




##
