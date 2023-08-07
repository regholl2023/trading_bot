# encoding: utf-8

# REST API
# (get these from signing into alpaca paper account)
API_KEY = "PKWV6OJQBH8Y3G6SE570"
API_SECRET_KEY = "raGALMJB1XdzDX1mAgLG3OFoz94BtgMJerZOKp1q"
API_URL = "https://paper-api.alpaca.markets"

# equity to spend per operation
maxSpendEquity = 5000

# boundaries for trading
stopLossMargin = 0.01
takeProfitMargin = 0.1

# limit price variability
maxVar = 0.1

# max attempts section
maxAttemptsCheckPosition = 10
maxAttemptsPrice = 5
maxAttemptsGeneralTrend = 10
maxAttemptsInstantTrend = 10
maxAttemptsRSI = 10
maxAttemptsStochastic = 10
maxAttemptsCancelPending = 5
maxAttemptsEnterPositionMode = 3

# sleep times section (seconds)
sleepTimeCheckPosition = 5
sleepTimePrice = 5
sleepTimeGeneralTrend = 60
sleepTimeInstantTrend = 30
sleepTimeRSI = 20
sleepTimeStochastic = 1
sleepTimeCancelPending = 5
sleepTimeEnterPositionMode = 20
