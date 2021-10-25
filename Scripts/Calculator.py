##

currency = "ethereum"  # Cryptocurrency planning to mine
hashRateNetwork = 651.424e12  # HashRate of the whole network
hashRate = 100e6  # HashRate of desired machine to use
meanTimePerBlock = 13.266007604562738  # Mean time in seconds of new block addition
currencyPerBlock = 2.2407362343389208  # Mean reward per block addition
secondsPerDay = 24 * 60 * 60  # Seconds per day
poolFee = 0.01  # Fee of pool in percentage (0 if no pool used)
powerPrice = 0.1  # USD/KWh
powerConsumption = 0.220  # KW used by machine
currencyPrice = 3057.99  # USD/currency

assert 0 <= poolFee <= 1

hashRateShare = hashRate / (hashRateNetwork+hashRate)
dailyBlocksAdded = secondsPerDay/meanTimePerBlock
dailyCurrenciesGiven = dailyBlocksAdded * currencyPerBlock

currencyPerDay = dailyCurrenciesGiven * hashRateShare * (1-poolFee)

revenue = currencyPerDay * currencyPrice

powerExpenses = 24 * powerConsumption * powerPrice

income = revenue - powerExpenses

print(f"Currency revenue: {currencyPerDay} {currency}")
print(f"Revenue: {revenue} USD")
print(f"Income: {income} USD")

##
