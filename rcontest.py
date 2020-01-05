import MCRcon.mcrcon as mcrcon
import socket, time, threading, re

ip = "starypc.lan"
port = 25575
password = "rconpass4321"
logLocation = "/home/grzesiek11/Testy/mnt/1/servers/minecraft/survival/logs/latest.log"

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def connect():
    print("Connecting to socket...")
    sock.connect((ip, port))
    print("Logging into rcon...")
    if mcrcon.login(sock, password):
        print("Done.")
    else:
        print("Invalid password!")

connect()

def parseLogLine(line):
    ret = re.findall("(?<=\[)(.+?)(?=\])", line)[:2]
    ret.append(re.search("(?<=: )(.*)(?=\n)", line).group())
    return ret

killThreads = False
killMain = False

def logReadLoop():
    global killThreads
    global killMain
    lastMessage = None
    """print("Loading latest.log...")
    if not logFile:
        print("Can't load latest.log!")
        return
    else:
        print("Done.")"""
    while not killThreads:
        logFile = open(logLocation)
        lastLine = list(logFile)[-1]
        if lastLine != lastMessage:
            lastMessage = lastLine
            if parseLogLine(lastMessage)[2] == "Stopping server":
                print("Server is stopping!")
                killMain = True

logReadLoopThread = threading.Thread(target = logReadLoop, daemon = True)
logReadLoopThread.start()

while not killMain:
    mcrcon.command(sock, "say say foo debugging 100")
    time.sleep(2)

killThreads = True

logReadLoopThread.join()