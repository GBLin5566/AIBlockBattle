from Bot.Strategies.MyStrategy import MyStrategy
def create(strategyType, game):
    switcher = {
        "my": MyStrategy(game)
    }

    strategy = switcher.get(strategyType.lower())

    return Planner(strategy)

class Planner:
    def __init__(self, strategy):
        self._strategy = strategy

    def makeMove(self):
        return self._strategy.choose()
