from agents import AgentManager
# from server import SocketCoordinator

class AgentCoordinator:
    def __init__(self):
        self.agents = []
        self.socket_agent_map = {}

    def add_agent(self, socket_manager):
        agent = AgentManager(socket_manager)
        self.agents.append(agent)
        self.socket_agent_map[socket_manager] = agent
    
    def remove_agent(self, socket_manager):
        agent = self.socket_agent_map[socket_manager]
        self.agents.remove(agent)
        del self.socket_agent_map[socket_manager]
        print("Removed agent", socket_manager.address)