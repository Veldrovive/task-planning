import asyncio
import websockets
import functools
from http import HTTPStatus
import os

from server import SocketCoordinator
from agents import AgentCoordinator

WEBSOCKET_PORT = 8765

socket_coordinator = SocketCoordinator()
agent_coordinator = AgentCoordinator(socket_coordinator)

MIME_TYPES = {
    "html": "text/html",
    "js": "text/javascript",
    "css": "text/css",
    "txt": "text/plain",
    "lua": "text/plain",
}

async def process_request(server_root, path, request_headers):
    """Serves a file when doing a GET request with a valid path."""
    server_root = os.path.join(server_root, 'static')

    if "Upgrade" in request_headers:
        return  # Probably a WebSocket connection

    if path == '/':
        path = '/index.html'

    response_headers = [
        ('Server', 'asyncio websocket server'),
        ('Connection', 'close'),
    ]

    # Derive full system path
    full_path = os.path.realpath(os.path.join(server_root, path[1:]))

    # Validate the path
    if os.path.commonpath((server_root, full_path)) != server_root or \
            not os.path.exists(full_path) or not os.path.isfile(full_path):
        print("HTTP GET {} 404 NOT FOUND".format(path))
        return HTTPStatus.NOT_FOUND, [], b'404 NOT FOUND'

    # Guess file content type
    extension = full_path.split(".")[-1]
    mime_type = MIME_TYPES.get(extension, "application/octet-stream")
    response_headers.append(('Content-Type', mime_type))

    # Read the whole file into memory and send it out
    body = open(full_path, 'rb').read()
    response_headers.append(('Content-Length', str(len(body))))
    print("HTTP GET {} 200 OK".format(path))
    return HTTPStatus.OK, response_headers, body

async def handle_connection(socket, path):
    await socket_coordinator.add_socket(socket)

async def main():
    handler = functools.partial(process_request, os.getcwd())

    import logging

    logger = logging.basicConfig(
        format="%(message)s",
        level=logging.DEBUG,
    )

    async with websockets.serve(
        handle_connection,
        'localhost',
        WEBSOCKET_PORT,
        # process_request=handler,
        ping_timeout=None,
        close_timeout=1,
        ping_interval=None,
        logger=logger,
    ):
        print("Listening on port {}".format(WEBSOCKET_PORT))
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
    