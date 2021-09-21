import player

class Game:
    def __init__(self, dono: int, tipo: str) -> object:
        ### ALOCA OS JOGADORES QUE ESTIVEREM JOGANDO
        self.players = []
        self.comecou = False
        self.tempo = 0
        self.dono = dono
        self.tipo = tipo

    def acabar_jogo(self):
        self.comecou = False
        self.tempo = 0

    def ja_entrou(self, name):
        for x in self.players:
            if x.nome == name:
                return x
        return None

    def entrar_player(self, player):
        pla = self.ja_entrou(player.nome)
        if pla is None:
            self.players.append(player)
            return True
        else:
            return False

    def sair_player(self, name):
        player = self.ja_entrou(name)
        if player is not None:
            self.players.remove(player)
            return True
        return False

    def comecar_jogo(self, tempo):
        self.comecou = True
        self.tempo = tempo

    def tickTempo(self):
        self.tempo -= 1
        return self.tempo > 0