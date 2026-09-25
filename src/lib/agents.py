class Agents:
    def __init__(self):
        self.agents_registry = {}

    def add_agent(self, agent_name, factory, system_prompt, description):
        self.agents_registry[agent_name] = {
            "factory": factory,
            "system_prompt": system_prompt,
            "description": description,
            "tools": []
        }

    def set_tools(self, agent_name, tools: list):
        self.agents_registry[agent_name]["factory"] = self.agents_registry[agent_name]["factory"].bind_tools(tools)
        self.agents_registry[agent_name]["tools"] = tools
    
    def add_graph(self, agent_name, graph):
        self.agents_registry[agent_name]["graph"] = graph

    def catalog(self):
        return "\n".join(f"- {name}: {info["description"]}" for name, info in self.agents_registry.items())

    def get(self):
        return self.agents_registry