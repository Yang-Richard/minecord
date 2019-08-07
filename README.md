# MineCord

**MineCord** is a bridge between Minecraft chat and Discord, using only rcon and server logs. It makes it work on Vanilla servers (no plugins needed).

## How does it work?

MineCord is divided to two parts: Discord and Minecraft.

Minecraft part uses server logs as input (reading messages from chat) and rcon as output (sending messages to chat).

Discord part uses Discord API for both input and output.

Discord input is connected with Minecraft output and Minecraft input is connected to Discord output. Simple

**rcon** is *remote console* protocol used by some games, including Minecraft. It can be used to send commands from any external program to game server console. MineCords sends tellraw commands to rcon, using it to view messages on chat.
