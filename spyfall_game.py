import discord

import game
import random
import asyncio
import os
import json
import sys


class Spyfall_Game(game.Game):
    def __init__(self, dono, tipo, mensagem, client):
        super().__init__(dono=dono, tipo=tipo)
        self.mensagem = mensagem
        self.client = client
        self.LOCATIONS_FILE = 'spyfall_locations.json'
        self.location = None
        self._game_data = None
        self.loc_list = []
        self.tempo = 480
        self.mensagensCriadas = []

    def embed_content(self, role, location):
        if role == "Espião":
            title = "Spyfall - Jogo"
            content = "Sua função é ---> **ESPIÃO** \n A localização é ---> *DESCUBRA*"
            return discord.Embed(title=title, description=content)
        elif role != "Espião":
            title = "Spyfall - Jogo"
            content = "Sua função é ---> **%s** \n A localização é ---> *%s*" % (role, location)
            return discord.Embed(title=title, description=content)

    def entrar_player(self, player):
        super().entrar_player(player)

    def sair_player(self, player):
        super().sair_player(player)

    async def comecar_jogo(self, tempo):
        if len(self.players) > 0: #2
            super().comecar_jogo(tempo=tempo)
            self.load()
            self.pegar_localizacao()
            self.definir_localizacao()
            self.definir_papeis()
            await self.enviar_mensagem(self.client)
            return True
        return False

    def definir_localizacao(self):
        if self._game_data != None:
            locations = self._game_data['locations']
            self.location = random.randint(0, len(locations) - 1)
        else:
            self.load()
            self.definir_localizacao()


    def definir_papeis(self):
        if self.location is not None:
            spy = random.randint(0, len(self.players) - 1)
            self.players[spy].tipo = "Espião"

            roles = self._game_data['locations'][self.location]['Roles']
            random.shuffle(roles)
            cur_role = 0
            for player in self.players:
                if player.tipo != "Espião":
                    player.tipo = roles[cur_role]
                    if cur_role <= (len(roles) - 1):
                        cur_role += 1
                    else:
                        cur_role = 0
        else:
            self.definir_localizacao()
            self.definir_papeis()


    def pegar_localizacao(self):
        del self.loc_list[:]
        for i in range(len(self._game_data['locations'])):
            self.loc_list.append(self._game_data['locations'][i]['Location'])

    async def acabar_jogo(self):
        super().acabar_jogo()
        for player in self.players:
            player.tipo = "vivo"

        for msg in self.mensagensCriadas:
            await msg.delete()

        self.mensagensCriadas.clear()


    def get_formatted_time(self):
        minutes, seconds = divmod(self.tempo, 60)
        return "{}:{:02d}".format(minutes, seconds)

    def load(self):
        if os.path.exists(self.LOCATIONS_FILE):
            with open(self.LOCATIONS_FILE, 'r', encoding='utf-8') as locations_file:
                self._game_data = json.load(locations_file)
            locations_file.close()
        else:
            print("O arquivo %s não existe ou não pode ser aberto")
            sys.exit(-1)

    async def revelar(self):
        reveal_title = 'Spyfall - Revelação'
        reveal_location = 'A localização era --> %s\n' % (self._game_data['locations'][self.location]['Location'])

        reveal_players = ''
        for player in self.players:
            reveal_players += '<@%s> --> %s\n' % (player.nome, player.tipo)

        reveal_content = reveal_location + reveal_players

        reveal_embed = discord.Embed(title=reveal_title, description=reveal_content)

        await self.mensagem.channel.send(embed=reveal_embed)
        await self.acabar_jogo()

    async def enviar_mensagem(self, client):
        message_channel = self.mensagem.channel

        mensagem1 = await message_channel.send("O jogo começou!")

        self.mensagensCriadas.append(mensagem1)

        for player in self.players:
            if player.tipo != 'Espião':
                user = client.get_user(player.nome)
                await user.send(embed=self.embed_content(player.tipo,
                                                    self._game_data['locations'][self.location][
                                                        'Location']))
            else:
                user = client.get_user(player.nome)
                await user.send(embed=self.embed_content(player.tipo,
                                                    'Descubra!'))

        location_title = "Spyfall - Lista de Localizações"
        location_content = ''
        for i in self.loc_list:
            location_content += "**%s**\n" % i

        loc_embed = discord.Embed(title=location_title, description=location_content)

        locs = await message_channel.send(embed=loc_embed)
        tempo = await message_channel.send('0:00')

        self.mensagensCriadas.append(locs)
        self.mensagensCriadas.append(tempo)

        while self.comecou and super().tickTempo():
            await tempo.edit(content='{}'.format(self.get_formatted_time()))
            await asyncio.sleep(1)
