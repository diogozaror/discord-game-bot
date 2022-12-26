import game
import random
import asyncio
import discord
import discord.ext.commands as commands


class Mafia_Game(game.Game, commands.Cog):
    def __init__(self, dono, tipo, mensagem, client):
        super().__init__(dono=dono, tipo=tipo)
        self.client = client
        self.qtdAssassinos = 1
        self.qtdPoliciais = 1
        self.qtdCurandeiros = 1
        self.mensagem = mensagem
        self.mensagensCriadas = []

    def embed_content(self, titulo, descricao):
        embed = discord.Embed(title=titulo, description=descricao)
        embed.set_author(name='Pox Game Bot', icon_url='https://i.imgur.com/tFxpOVj.jpeg')
        embed.set_footer(text='PoxToc Games and Company ')

        return embed

    def entrar_player(self, player):
        super().entrar_player(player)

    def sair_player(self, player):
        super().sair_player(player)

    async def comecar_jogo(self, tempo):
        if len(self.players) > (self.qtdAssassinos + self.qtdPoliciais+self.qtdCurandeiros)+1:
            super().comecar_jogo(tempo=tempo)
            self.definir_papeis()
            await self.enviar_painel()
            await self.enviar_mensagem()
            return True
        return False

    def definir_papeis(self):
        for player in self.players:
            player.estado = 'vivo'

        random.shuffle(self.players)

        for x in range(len(self.players)):
            self.players[x].tipo = 'Civil'
            if x < self.qtdAssassinos:
                self.players[x].tipo = 'Assassino'
            if self.qtdAssassinos < x <= self.qtdAssassinos + self.qtdPoliciais:
                self.players[x].tipo = 'Policial'
            if self.qtdAssassinos + self.qtdPoliciais < x <= self.qtdAssassinos + self.qtdPoliciais + self.qtdCurandeiros:
                self.players[x].tipo = 'Curandeiro'

    async def acabar_jogo(self, vencedor):
        super().acabar_jogo()

        if vencedor == 'Civil':
            await self.mensagem.channel.send(embed=self.embed_content('**O jogo acabou!**', 'A população ganhou!'))
        else:
            await self.mensagem.channel.send(embed=self.embed_content('**O jogo acabou!**', 'Os assassinos ganharam!'))

        for msg in self.mensagensCriadas:
            await msg['msg'].delete(delay=10.0)
        self.mensagensCriadas.clear()

    def get_formatted_time(self):
        minutes, seconds = divmod(self.tempo, 60)
        return "{}:{:02d}".format(minutes, seconds)

    def quantidadeAssasinos(self):
        qtd = 0
        for x in self.players:
            if x.estado == 'vivo':
                if x.tipo == 'Assassino':
                    qtd += 1

        return qtd

    def quantidadeCivis(self):
        qtd = 0
        for x in self.players:
            if x.estado == 'vivo':
                if x.tipo == 'Civil' or x.tipo == 'Policial' or x.tipo == 'Curandeiro':
                    qtd += 1

        return qtd

    async def retirar_player(self, player):
        msg = await self.mensagem.channel.send('O jogador <@{}> morreu! \nSua função era: {}'
                                               .format(player.nome, player.tipo))

        nome = f'retirada_{player.nome}'

        self.mensagensCriadas.append({'nome': nome, 'msg': msg})

        player.estado = 'morto'

        await self.atualizar_painel()

        if self.quantidadeAssasinos() == 0:
            await self.acabar_jogo('Civil')
        elif self.quantidadeCivis() == 0:
            await self.acabar_jogo('Assassino')

    async def enviar_mensagem(self):
        message_channel = self.mensagem.channel

        papeis = await message_channel.send(embed=self.embed_content('**Jogo Iniciado!**',
                                                                     'Os papeis foram enviados a cada jogador!\n'
                                                                     'Olhe para o privado para saber seu papel!\n'))
        tempo = await message_channel.send('{}'.format(self.get_formatted_time()))

        self.mensagensCriadas.append({'nome': 'papeis', 'msg': papeis})
        self.mensagensCriadas.append({'nome': 'tempo', 'msg': tempo})

        for x in range(len(self.players)):
            if self.players[x].tipo == 'Assassino':
                user = await self.client.fetch_user(self.players[x].nome)
                msg = await user.send(embed=self.embed_content(self.players[x].tipo, "Você é um ***assassino***! \n "
                                                                                     "Tudo que você digitar nesse canal\n"
                                                                                     "será enviado para o mestre e para\n"
                                                                                     "o seu parceiro assassino (caso exista)!"))

                self.mensagensCriadas.append({'nome': user, 'msg': msg})
                self.players[x].adicionarDMChannel(msg.channel)
            if self.players[x].tipo == 'Policial':
                user = await self.client.fetch_user(self.players[x].nome)
                msg = await user.send(embed=self.embed_content(self.players[x].tipo, "Você é um ***policial***! \n "
                                                                                     "Tudo que você digitar nesse canal\n"
                                                                                     "será enviado para o mestre e para\n"
                                                                                     "o seu parceiro policial (caso exista)!"))

                self.mensagensCriadas.append({'nome': user, 'msg': msg})
                self.players[x].adicionarDMChannel(msg.channel)
            if self.players[x].tipo == 'Curandeiro':
                user = await self.client.fetch_user(self.players[x].nome)
                msg = await user.send(embed=self.embed_content(self.players[x].tipo, "Você é um ***curandeiro***! \n "
                                                                                     "Tudo que você digitar nesse canal\n"
                                                                                     "será enviado para o mestre e para\n"
                                                                                     "o seu parceiro policial (caso exista)!"))
                self.mensagensCriadas.append({'nome': user, 'msg': msg})
                self.players[x].adicionarDMChannel(msg.channel)
            if self.players[x].tipo == 'Civil':
                user = await self.client.fetch_user(self.players[x].nome)
                msg = await user.send(
                    embed=self.embed_content(self.players[x].tipo, "Você é um ***civil***! \n Boa sorte!"))

                self.mensagensCriadas.append({'nome': user, 'msg': msg})
                self.players[x].adicionarDMChannel(msg.channel)

        while self.comecou and super().tickTempo():
            await tempo.edit(content='{}'.format(self.get_formatted_time()))
            await asyncio.sleep(1)

    def getEmojis(self):
        emoji0 = "0️⃣"
        emoji1 = "1️⃣"
        emoji2 = "2️⃣"
        emoji3 = "3️⃣"
        emoji4 = "4️⃣"
        emoji5 = "5️⃣"
        emoji6 = "6️⃣"
        emoji7 = "7️⃣"
        emoji8 = "8️⃣"
        emoji9 = "9️⃣"

        emojis = []
        emojis.append(emoji0)
        emojis.append(emoji1)
        emojis.append(emoji2)
        emojis.append(emoji3)
        emojis.append(emoji4)
        emojis.append(emoji5)
        emojis.append(emoji6)
        emojis.append(emoji7)
        emojis.append(emoji8)
        emojis.append(emoji9)

        return emojis

    async def enviar_painel(self):
        mestre =await self.client.fetch_user(self.dono)

        if mestre is None:
            return

        mensagem_enviar = ""
        for x in range(len(self.players)):
            mensagem_enviar += f"{x}. <@{self.players[x].nome}> [{self.players[x].tipo}] - {self.players[x].estado} \n"

        painel = await mestre.send(embed=
                                   self.embed_content('Painel de Mortes!',
                                                      "Você como mestre escolhe as pessoas que serão eliminadas!\n" +
                                                      "***ATENÇÃO: Você pode matar a qualquer momento então preste atenção!***\n" +
                                                      mensagem_enviar))

        self.mensagensCriadas.append({'nome': 'painel', 'msg': painel})

        emojis = self.getEmojis()

        for x in range(len(self.players)):
            await painel.add_reaction(emojis[x])

    async def atualizar_painel(self):
        dic = {}
        for men in self.mensagensCriadas:
            if men['nome'] == 'painel':
                dic = men
        msg = dic['msg']

        mensagem_enviar = ""
        for x in range(len(self.players)):
            mensagem_enviar += f"{x}. <@{self.players[x].nome}> [{self.players[x].tipo}] - {self.players[x].estado} \n"

        await msg.edit(embed=
                       self.embed_content('Painel de Mortes!',
                                          "Você como mestre escolhe as pessoas que serão eliminadas!\n" +
                                          "***ATENÇÃO: Você pode matar a qualquer momento então preste atenção!***\n" +
                                          mensagem_enviar))

        emojis = self.getEmojis()

        for x in range(len(self.players)):
            await msg.add_reaction(emojis[x])
