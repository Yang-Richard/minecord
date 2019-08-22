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
    for attachment in message.attachments:
        messageText += f" {attachment.url}"
    command = """tellraw @a ["",{"text":"["},{"text":"%s","color":"dark_aqua"},{"text":" | "},{"text":"#%s","color":"dark_aqua"},{"text":"] %s"}]""" % (message.author.display_name, message.channel.name, messageText)
    mcrcon.command(sock, command)

def parseLogLine(line):
    parts = []
    start = 0
    for i in range(2):
        lIndex = line.find('[', start)
        start = lIndex + 1
        rIndex = line.find(']', start)
        start = rIndex + 1
        parts.append(line[lIndex + 1:rIndex])
    parts.append(line[start + 2:].replace('\n', ''))
    return parts

def parseChatMessage(messageType, content):
    if messageType != "Server thread/INFO":
        return False
    match = re.search("(?<=<)(.*)(?=>)", content)
    nick = match.group()
    message = content[match.end() + 2:]
    return nick, message

@tasks.loop()
async def toDiscord():
    global lastMessage
    with open(config['servers'][0]['log']) as logfile:
        lastLine = list(logfile)[-1]
        if lastMessage != lastLine:
            lastMessage = lastLine
            time, messageType, content = parseLogLine(lastLine)
            if parseChatMessage(messageType, content):
                nick, message = parseChatMessage(messageType, content)
                for channelID in config["minecraftToDiscordChannels"]:
                    await bot.get_channel(channelID).send(f"<{nick}> {message}")

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
    if message.content == "mc!status":
        query = server.query()
        motd = re.sub("§\w", "", query.motd)
        players = query.players.names
        playersStr = ""
        for player in players:
            playersStr += player
            if not player == players[len(players) - 1]:
                playersStr += ", "
        statusMessage = f"""**{motd}**

        **Player count:** {query.players.online}/{query.players.max}
        **Players**: {playersStr}
        **Version:**: {query.software.version}
        **World**: {query.map}
        **Ping:** {server.ping()}ms"""
        await message.channel.send(embed = discord.Embed(title = config['servers'][0]['name'], description = statusMessage))

bot.run(config["key"])
sock.close()