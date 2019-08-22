import discord
from discord.ext import tasks
import MCRcon.mcrcon as mcrcon
import socket, json, os, shutil
from mcstatus import MinecraftServer

if os.path.exists('config.json'):
    with open('config.json') as file:
        config = json.load(file)
else:
    shutil.copy('config.json.template', 'config.json')
    print("No configuration detected. Please, edit config.json and run this program again.")
    exit()

bot = discord.Client()
server = MinecraftServer.lookup("localhost:25565")

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((config['rcon']['IP'], config['rcon']['port']))
mcrcon.login(sock, config['rcon']['password'])

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
    lNick = content.find('<')
    if lNick == -1:
        return False
    rNick = content.find('>')
    nick = content[lNick + 1:rNick]
    message = content[rNick + 2:]
    return nick, message

@tasks.loop()
async def toDiscord():
    global lastMessage
    with open(config['minecraftLog']) as logfile:
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
        message.channel.send(str(server.query))

bot.run(config["key"])
sock.close()