import game


games = []


def getgameowned(id):
    for x in range(len(games)):
        if games[x].dono == id:
            return games[x]
        elif games[x].dono is None:
            remover(game)

    return None


def getgamecurrent(id):
    for x in range(len(games)):
        for player in games[x].players:
            if player.nome == id:
                return games[x]

    return None


def adicionar(game):
    if getgameowned(game.dono) is not None:
        return False

    games.append(game)
    return True

def remover(game):
    a = getgameowned(game.dono)
    if a is not None:
        del a
        return True
    return False
