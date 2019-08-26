import discord
from discord.ext import tasks
import MCRcon.mcrcon as mcrcon
import socket, json, os, shutil, re
from mcstatus import MinecraftServer

if os.path.exists('config.json'):
    with open('config.json') as file:
        config = json.load(file)
else:
    shutil.copy('config.json.template', 'config.json')
    print("No configuration detected. Please, edit config.json and run this program again.")
    exit()

bot = discord.Client()
server = MinecraftServer.lookup(f"{config['servers'][0]['IP']}:{config['servers'][0]['query']}")

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((config['servers'][0]['IP'], config['servers'][0]['rcon']['port']))
mcrcon.login(sock, config['servers'][0]['rcon']['password'])

lastMessage = None

def toMinecraft(message):
    messageText = message.clean_content
    customEmoji = re.compile("<:.*:\d*>")
    emojiName = re.compile(":(?<=:)(.*)(?=:):")
    for emoji in customEmoji.findall(messageText):
        messageText = messageText.replace(emoji, emojiName.search(emoji).group())
    for attachment in message.attachments:
        messageText += f" {attachment.url}"
    command = """tellraw @a ["",{"text":"["},{"text":"%s","color":"dark_aqua"},{"text":" | "},{"text":"#%s","color":"dark_aqua"},{"text":"] %s"}]""" % (message.author.display_name, message.channel.name, messageText)
    mcrcon.command(sock, command)

def parseLogLine(line):
    ret = re.findall("(?<=\[)(.+?)(?=\])", line)[:2]
    ret.append(re.search("(?<=: )(.*)(?=\n)", line).group())
    return ret

def parseChatMessage(messageType, content):
    if messageType != "Server thread/INFO":
        return False
    nickMatch = re.search("(?<=<)(.*)(?=>)", content)
    if nickMatch is None:
        return False
    nick = nickMatch.group()
    message = content[nickMatch.end() + 2:]
    mentions = re.findall("@.*?#\d{4}", message)
    for mention in mentions:
        for member in bot.get_all_members():
            if f"@{member.name}#{member.discriminator}" == mention:
                message = message.replace(mention, member.mention)
    return nick, message

def parseEvents(messageType, content):
    if messageType != "Server thread/INFO":
        return False
    words = content.split(' ')
    if re.search(".+? joined the game", content) != None:
        return 1, [words[0]]
    elif re.search(".+? left the game", content) != None:
        return 2, [words[0]]
    elif words[0] == "*":
        return 3, [words[1], words[2:]]

async def sendToDiscord(message):
    for channelID in config["minecraftToDiscordChannels"]:
        await bot.get_channel(channelID).send(message)

@tasks.loop()
async def toDiscord():
    global lastMessage
    with open(config['servers'][0]['log']) as logfile:
        lastLine = list(logfile)[-1]
        if lastMessage != lastLine:
            lastMessage = lastLine
            consoleChannel = config['servers'][0]['consoleChannel']
            if consoleChannel != -1:
                await bot.get_channel(consoleChannel).send(lastLine)
            time, messageType, content = parseLogLine(lastLine)
            chatMessage = parseChatMessage(messageType, content)
            if chatMessage:
                nick, message = chatMessage
                await sendToDiscord(f"<{nick}> {message}")
            else:
                events = parseEvents(messageType, content)
                if events:
                    event, parameters = events
                    if event == 1:
                        await sendToDiscord(f":heavy_plus_sign: **{parameters[0]}** joined.")
                    elif event == 2:
                        await sendToDiscord(f":heavy_minus_sign: **{parameters[0]}** left.")
                    elif event == 3:
                        await sendToDiscord(f"**{parameters[0]}** {parameters[1]}")

@bot.event
async def on_ready():
    print(f'MineCord logged in as {bot.user}.')
    toDiscord.start()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.channel.id in config["discordToMinecraftChannels"]:
        toMinecraft(message)
    if message.channel.id == config['servers'][0]['consoleChannel']:
        mcrcon.command(sock, message.content)
    if message.content == "mc!status":
        query = server.query()
        motd = re.sub("§\w", "", query.motd)
        players = query.players.names
        playersStr = ""
        for player in players:
            playersStr += player
            if not player == players[len(players) - 1]:
                playersStr += ", "
        statusMessage = f"""**{motd}**\n
        **Player count:** {query.players.online}/{query.players.max}{f'''
        **Players**: {playersStr}''' if query.players.online > 0 else ''}
        **Version:**: {query.software.version}
        **World**: {query.map}
        **Ping:** {server.ping()}ms"""
        await message.channel.send(embed = discord.Embed(title = config['servers'][0]['name'], description = statusMessage))

bot.run(config["key"])
sock.close()
