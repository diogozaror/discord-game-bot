class Player:
    def __init__(self, nome, tipo):
        self.nome = nome
        self.tipo = tipo
        self.dmchannel = None
        self.estado = 'vivo'

    def adicionarDMChannel(self, id):
        self.dmchannel = id

    def getDMChannel(self):
        return self.dmchannel

    def setEstado(self, estado):
        self.estado = estado

    def getEstado(self):
        return self.estado
