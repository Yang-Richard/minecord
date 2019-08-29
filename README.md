# MineCord

**MineCord** is a bridge between Minecraft chat and Discord, using only rcon and server logs. It makes it work on Vanilla servers (no plugins needed).

## Features

- Sending Minecraft messages to Discord
- Sending Discord messages to Minecraft
- Sending Minecraft events to Discord:
    - When player joins.
    - When player leaves.
    - /me statuses.
- Bot commands:
    - `mc!status` - check server status.
- Console channel - set up private console channel on Discord, where you can enter commands and read servers console.

## Coming soon

- `mc!stats` command for checking player statistics.
- Multiple Minecraft servers support.
- More events.
- More options in config.
- Full configuration tutorial.
- Fixing bugs.
- Bedrock support

## Compability

**Minecraft**: Java Edition (Bedrock is WIP) 1.14.x or older with the same log format and with rcon. If you really play on version that is so old it doesn't work, open an issue.

**Python**: 3.6 or higher, tested on 3.7.

**discord.py**: 1.3.0 (higher should work)

## How to use

1. Install Python (3.6 or higher) on your server if you haven't already.
2. Clone this repository with submodules:

```sh
git clone --recurse-submodules --depth=1 https://gitlab.com/grzesiek11/minecord.git
```

3. `cd` onto the repository.
4. Run the program:

```sh
python3 main.py
```

It will close soon after running it and will generate a config file.

5. Open `config.json` in your favourite text editor.

Change `"Minecraft Server"` to your server name.

Change `"rconpassword"` to anything you can remember (it even doesn't need to be strong).

Change `"/path/to/server/logs/latest.log"` to path of latest.log (it usually is the Minecraft server path and `logs/latest.log`).

Change `-1` in `"consoleChannel"` to your console channel ID, or don't change it if you don't need one.

Change `"bot key"` to your bot key.

Add channels (their IDs) that you want MineCord to post messages from on Minecraft to `"discordToMinecraftChannels"`.

Add channels that MineCord will send Minecraft chat to to `"minecraftToDiscordChannels"`.

6. Go to your server directory and open `server.properties` in your favourite text editor.

Change `rcon.password` to the password you set in MineCord config.

Change `enable-rcon` to `true`.

Change `enable-query` to `true`.

7. You did it! Now you can go back to the MineCord directory and run it again.

```sh
python3 main.py
```

## How does it work?

MineCord is divided to two parts: Discord and Minecraft.

Minecraft part uses server logs as input (reading messages from chat) and rcon as output (sending messages to chat).

Discord part uses Discord API for both input and output.

Discord input is connected with Minecraft output and Minecraft input is connected to Discord output. Simple

## What is rcon?

**rcon** is *remote console* protocol used by some games, including Minecraft. It can be used to send commands from any external program to game server console. MineCords sends tellraw commands to rcon, using it to view messages on chat.
