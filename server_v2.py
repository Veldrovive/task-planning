from simple_websocket_server import WebSocketServer
from typing import List
from server import MultiThreadTopicSocketManager
from agents import AgentCoordinator
import asyncio
from http.server import HTTPServer, SimpleHTTPRequestHandler
import functools
import threading

TESTING = False

if TESTING:
    print("*****************\nRUNNING IN TESTING MODE\n*****************\n")
    from worlds.__world import test as test_world
    test_world()
    exit()


WEBSOCKET_PORT = 8765
STATIC_PORT = WEBSOCKET_PORT + 1

agent_coordinator = AgentCoordinator()

clients_to_initialize: List[MultiThreadTopicSocketManager] = []


async def handle_clients_loop():
    while True:
        if len(clients_to_initialize) > 0:
            print("Initializing client")
            client = clients_to_initialize.pop()
            agent_coordinator.add_agent(client)
            client.add_on_disconnect_callback(agent_coordinator.remove_agent)
        
        if len(agent_coordinator.agents) > 0:
            for agent in agent_coordinator.agents:
                socket: MultiThreadTopicSocketManager = agent.socket_manager
                await socket.handle_callbacks()
        
        await asyncio.sleep(0.001)

def start_socket_server():
    def create_socket(server, sock, address):
        socket = MultiThreadTopicSocketManager(server, sock, address)
        clients_to_initialize.append(socket)
        return socket

    server = WebSocketServer('127.0.0.1', WEBSOCKET_PORT, create_socket)

    print("Starting socket server")
    server.serve_forever()

def serve_static():
    SimpleHTTPRequestHandler.extensions_map[".lua"] = "text/plain"
    RequestHandler = functools.partial(SimpleHTTPRequestHandler, directory='static')
    httpd = HTTPServer(('127.0.0.1', STATIC_PORT), RequestHandler)

    print("Starting static server")
    httpd.serve_forever()

async def main():
    # Start the socket and static threads
    asyncio.ensure_future(handle_clients_loop())
    socket_thread = threading.Thread(target=start_socket_server, daemon=True)
    static_thread = threading.Thread(target=serve_static, daemon=True)
    socket_thread.start()
    static_thread.start()
    await asyncio.Future()

asyncio.run(main())