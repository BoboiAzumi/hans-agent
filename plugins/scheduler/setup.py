from plugins.scheduler.service import scheduler, tool_call

plugin = {
    "interface": scheduler.graph_bind,
    "tool": tool_call
}