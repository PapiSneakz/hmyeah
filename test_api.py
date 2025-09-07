import ccxt

exchange = ccxt.coinbase({
    'apiKey': "organizations/ee5e6607-a33d-47f7-bd13-a27289a46cc9/apiKeys/1bdacbb3-2cea-4aa2-9802-bbdd6bfd9414",
    'secret': "\nMHcCAQEEIIrkjLwvWv6wo9UO//m2w1sOs/q6xFnf0uMbtumI9K7QoAoGCCqGSM49\nAwEHoUQDQgAEaGggzoWzCaodNAEFYd6hxpCp24EemgAkEEpuGRcxCU9u5gPXI2b3\nGh6dErZ07a1dbn9qqeC8pSBTd81r7T1QHg==\n-----END EC PRIVATE KEY-----\n",
    'password': "Fristie564!",
    'enableRateLimit': True
})

markets = exchange.fetch_markets()
print(markets[:2])
