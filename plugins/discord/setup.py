from plugins.discord.service import bot, tool_call

plugin = {
    "interface": bot.graph_bind,
    "tool": tool_call
}