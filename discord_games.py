import discord
import asyncio
import json
import os
from mafia_game import Mafia_Game
from spyfall_game import Spyfall_Game
import manager
from player import Player

if os.path.exists('config.json'):
    with open('config.json', 'r') as configs:
        configs = json.load(configs)

bot_token = configs['discord']['token']
bot_trigger = configs['discord']['trigger']

client = discord.Client()


def embed_content(titulo, descricao):
    embed = discord.Embed(title=titulo, description=descricao)
    embed.set_author(name='Pox Game Bot', icon_url='https://i.imgur.com/tFxpOVj.jpeg')
    embed.set_footer(text='PoxToc Games and Company ')

    return embed


@client.event
async def on_raw_reaction_add(event):
    channel_id = event.channel_id
    emoji = event.emoji
    user = client.get_user(event.user_id)
    msg_id = event.message_id

    if user is None:
        return

    if user == client.user:
        return

    game = manager.getgameowned(event.user_id)

    if game is None:
        return

    if game.tipo != 'Mafia':
        return

    msg = await client.get_channel(channel_id).fetch_message(msg_id)

    if emoji is None:
        return

    emotes = game.getEmojis()

    for x in range(len(game.getEmojis())):
        if emotes[x] == emoji.name:
            player = game.players[x]
            if player is not None:
                if player.estado == 'vivo':
                    await game.retirar_player(player)



@client.event
async def on_ready():
    print("--------------------")
    print("Nome do Bot: %s" % client.user)
    print("User ID do Bot: %s" % client.user.id)
    print("--------------------")


@client.event
async def on_message(message):
    message_delete = message
    message_author = message.author
    message_author_id = message.author.id
    message_channel = message.channel
    message_content = message.content.lower()

    if message_content.startswith(bot_trigger + 'criar'):
        args = message_content.split(" ")
        if len(args) > 1:
            if args[1] == 'mafia':
                jogo = Mafia_Game(message_author_id, 'Mafia', message, client)

                #client.user.add_cog(jogo)
                resposta = manager.adicionar(jogo)
                if resposta:
                    await message_channel.send(embed=embed_content('Sucesso',
                                                                   'Seu jogo de Mafia foi criado! \n'
                                                                   'Você é o mestre! \n'
                                                                   'Para os jogadores entrarem basta digitar: \n'
                                                                   + bot_trigger + 'entrar <@%s> \n' % message_author_id +
                                                                   'Há 1 policial e 1 asssassino configurado por padrão.\n'
                                                                   'Para modificar isso use ' + bot_trigger +
                                                                   'configuracao mafia policial/assassino/curandeiro [quantidade]'))
                else:
                    await message_channel.send(embed=embed_content('Erro', 'Você já tem um jogo criado!'))
            elif args[1] == 'spyfall':
                jogo = Spyfall_Game(message_author_id, 'Spyfall', message, client)
                resposta = manager.adicionar(jogo)
                if resposta:
                    player = Player(message_author_id, 'None')
                    jogo.entrar_player(player)
                    await message_channel.send(embed=embed_content('Sucesso',
                                                                   'Seu jogo de Spyfall foi criado! \n'
                                                                   'Para os jogadores entrarem basta digitar: \n'
                                                                   + bot_trigger + 'entrar <@%s> \n' % message_author_id))
                else:
                    await message_channel.send(embed=embed_content('Erro', 'Você já tem um jogo criado!'))
            else:
                await message_channel.send(embed=embed_content('Erro', 'Comando inválido! \nDigite'
                                                                       ' ' + bot_trigger + 'criar <spyfall/mafia>'))
        else:
            await message_channel.send(embed=embed_content('Erro', 'Comando inválido! \nDigite'
                                                                   ' ' + bot_trigger + 'criar <spyfall/mafia>'))
    elif message_content.startswith(bot_trigger + 'entrar'):
        args = message_content.split(" ")
        if len(args) > 1:
            user_id = (args[1][2:len(args[1]) - 1])
            user_id = user_id.replace('!', '')
            user_id = user_id.replace('e', '')
            user_id = int(user_id)
            user = client.get_user(user_id)
            if user is not None:
                game = manager.getgameowned(user_id)
                if game is not None:
                    player = Player(message_author_id, 'None')
                    game.entrar_player(player)

                    await message_channel.send(embed=embed_content('Sucesso', 'O jogador <@{}> entrou no jogo '
                                                                                  'de <@{}> !'
                                                                       .format(message_author_id, user_id)))
                else:
                    await message_channel.send(embed=embed_content('Erro', '<@{}> não criou um jogo!'.format(user_id)))
            else:
                await message_channel.send(embed=embed_content('Erro', 'Esse jogador não foi encontrado!'
                                                               .format(user_id)))
        else:
            await message_channel.send(embed=embed_content('Erro', 'Comando inválido! \nDigite'
                                                                   ' ' + bot_trigger + 'entrar @Dono'))
    elif message_content.startswith(bot_trigger + 'sair'):
        args = message_content.split(" ")
        if len(args) > 1:
            user_id = (args[1][2:len(args[1]) - 1])
            user_id = user_id.replace('!', '')
            user_id = int(user_id)
            user = client.get_user(user_id)
            if user is not None:
                game = manager.getgameowned(user_id)
                if game is not None:
                    player = game.ja_entrou(message_author_id)
                    if player is not None:
                        resposta = game.sair_player(player.nome)
                        if resposta:
                            await message_channel.send(embed=embed_content('Sucesso', 'O jogador <@{}> saiu no jogo de'
                                                                                      '<@{}>!'
                                                                           .format(message_author_id, game.dono)))
                        else:
                            await message_channel.send(embed=embed_content('Erro', 'Não foi possível sair do jogo!'))
                    else:
                        await message_channel.send(embed=embed_content('Erro', 'O jogador <@{}> não está no jogo!'
                                                                       .format(message_author_id)))

                else:
                    await message_channel.send(embed=embed_content('Erro', '<@{}> não criou um jogo!'.format(user_id)))
            else:
                await message_channel.send(embed=embed_content('Erro', 'Esse jogador não foi encontrado!'
                                                               .format(user_id)))
        else:
            await message_channel.send(embed=embed_content('Erro', 'Comando inválido! \nDigite'
                                                                   ' ' + bot_trigger + 'sair @Dono'))
    elif message_content.startswith(bot_trigger + 'matar'):
        args = message_content.split(" ")
        if len(args) > 1:
            user_id = (args[1][2:len(args[1]) - 1])
            user_id = user_id.replace('!', '')
            user_id = int(user_id)
            user = client.get_user(user_id)
            if user is not None:
                game = manager.getgameowned(message_author_id)
                if game is not None:
                    if game.tipo == 'Mafia':
                        player = game.ja_entrou(user_id)
                        if player is not None:
                            await game.retirar_player(player)
                        else:
                            await message_channel.send(embed=embed_content('Erro', 'O jogador <@{}> não está no jogo!'
                                                                           .format(user_id)))
                    else:
                        await message_channel.send(embed=embed_content('Erro', 'Não é possível retirar jogadores nesse'
                                                                               'modo de jogo!'))
                else:
                    await message_channel.send(embed=embed_content('Erro', 'Você não criou um jogo!'.format(user_id)))
            else:
                await message_channel.send(embed=embed_content('Erro', 'Esse jogador não foi encontrado!'
                                                               .format(user_id)))
        else:
            await message_channel.send(embed=embed_content('Erro', 'Comando inválido! \nDigite'
                                                                   ' ' + bot_trigger + 'retirar @Jogador'))
    elif message_content.startswith(bot_trigger + 'configuracao'):
        args = message_content.split(" ")
        if len(args) > 3:
            if args[1]== 'mafia':
                if args[2] == 'policial' or args[2]=='assassino' or args[2]=='curandeiro':
                    if args[3].isnumeric():
                        user_id = message_author_id
                        if user_id is not None:
                            game = manager.getgameowned(user_id)
                            if game is not None:
                                if game.tipo == 'Mafia':
                                    num = int(args[3])
                                    if 3 >= num > 0:
                                        if args[2]=='policial':
                                            game.qtdPoliciais = num
                                        elif args[2]=='assassino':
                                            game.qtdAssassinos = num
                                        elif args[2]=='curandeiro':
                                            game.qtdCurandeiros = num

                                        await message_channel.send(embed=embed_content('Sucesso', 'A configuração foi salva!'))
                                    else:
                                        await message_channel.send(
                                            embed=embed_content('Erro', 'O número deve ser entre 0 e 3!'))
                                else:
                                    await message_channel.send(embed=embed_content('Erro', 'Não é possível usar essa configuração'
                                                                                           'nesse jogo!'))
                            else:
                                await message_channel.send(embed=embed_content('Erro', 'Você não criou um jogo!'.format(user_id)))
                        else:
                            await message_channel.send(embed=embed_content('Erro', 'Esse jogador não foi encontrado!'
                                                                           .format(user_id)))
                    else:
                        await message_channel.send(
                            embed=embed_content('Erro', f'Número {args[3]} de mafia não corresponde!'))
                else:
                    await message_channel.send(embed=embed_content('Erro', f'Configuração {args[2]} de mafia não encontrada!'))
            else:
                await message_channel.send(embed=embed_content('Erro', f'Configuração para {args[1]} não encontrada!'))
        else:
            await message_channel.send(embed=embed_content('Erro', 'Comando inválido! \nDigite'
                                                                   ' ' + bot_trigger + 'configuracao [jogo] [complemento] [valor]'))
    elif message_content.startswith(bot_trigger + "comecar"):
        game = manager.getgameowned(message_author_id)
        if game is not None:
            if game.dono == message_author_id:
                resposta = await game.comecar_jogo((10 + len(game.players)*2) * 60)
                if not resposta:
                    await message_channel.send(embed=embed_content('Erro', 'Não há jogadores suficientes!'))
                    return
            else:
                await message_channel.send(embed=embed_content('Erro', 'Você não é o dono!'))
        else:
            await message_channel.send(embed=embed_content('Erro', 'Você não tem um jogo criado!'))
    elif message_content.startswith(bot_trigger + 'revelar'):
        game = manager.getgameowned(message_author_id)
        if game is not None:
            if game.dono == message_author_id:
                if game.tipo == 'Spyfall':
                    await game.revelar()
            else:
                await message_channel.send(embed=embed_content('Erro', 'Você não é o dono!'))
        else:
            await message_channel.send(embed=embed_content('Erro', 'Você não tem um jogo criado!'))
    else:
        game = manager.getgamecurrent(message_author_id)
        if game is None or game.tipo != 'Mafia':
            return

        for player in game.players:
            if message_channel == player.getDMChannel():
                if player.nome == message_author_id:
                    mestre = client.get_user(game.dono)
                    await mestre.send(f'<@{player.nome}> ({player.tipo}): {message_content}')

                    if player.tipo != 'Civil':
                        for player2 in game.players:
                            if player2.tipo == player.tipo and player2.nome != player.nome:
                                playerTo = client.get_user(player2.nome)
                                await playerTo.send(f'<@{player.nome}> ({player.tipo}): {message_content}')


client.run(bot_token)


