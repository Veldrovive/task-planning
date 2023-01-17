import asyncio
import websockets
from typing import Callable, Any, Coroutine, Optional
from models import TopicMessage
from uuid import uuid4

MessageCallbackType = Callable[[str], Coroutine]

class SocketManager:
    def __init__(self, socket):
        self.socket = socket
        self.callbacks = []

    async def start_listener(self):
        while True:
            try:
                print("Waiting for message")
                msg = await self.socket.recv()
                print('Got message', msg)
                if msg == 'ping':
                    print("Got ping")
                    continue
                tasks = []
                for callback in self.callbacks:
                    tasks.append(asyncio.create_task(callback(msg)))
                # await asyncio.gather(*tasks)  # Whoops, this means we could not process messages while waiting for a response
            except websockets.exceptions.ConnectionClosed:
                print("Connection closed")
                break

    def add_callback(self, callback: MessageCallbackType):
        self.callbacks.append(callback)

    def remove_callback(self, callback: MessageCallbackType):
        self.callbacks.remove(callback)

    async def send_message(self, message: str):
        await self.socket.send(message)

TopicCallbackType = Callable[[str, Any], Coroutine]

class TopicSocketManager(SocketManager):
    """
    A special case of the SocketManager that expects messages to be of the TopicMessage type which allows for more complex communication
    I expect only one callback to be registered for each topic so I will assume that simplification
    """
    def __init__(self, socket):
        super().__init__(socket)
        self.add_callback(lambda message: self.handle_topic_message(TopicMessage.parse_raw(message)))
        self.topic_callbacks: dict[str, TopicCallbackType] = {}

    async def handle_topic_message(self, message: TopicMessage):
        print('Got topic message', message.topic, message.message)
        # print('Have handlers for topics:', list(self.topic_callbacks.keys()))
        if message.topic in self.topic_callbacks:
            try:
                await self.topic_callbacks[message.topic](message.topic, message.message)
            except Exception as e:
                print('Error in topic callback while handling topic message', message.topic, e)

    def add_topic_callback(self, topic: str, callback: TopicCallbackType):
        self.topic_callbacks[topic] = callback

    def remove_topic_callback(self, topic: str):
        del self.topic_callbacks[topic]

    async def await_response_once(self, topic: str):
        """
        Waits for a message with the topic and returns its message
        This converts the callback into a future to make it easier to use with await
        """
        future = asyncio.Future()

        async def callback(_, message):
            future.set_result(message)

        self.add_topic_callback(topic, callback)
        res = await future
        self.remove_topic_callback(topic)
        return res

    async def send(self, message: Any, topic: str):
        """
        Sends a message as a topic
        """
        await self.send_message(TopicMessage(topic=topic, message=message).json())

    async def send_and_await_response(self, message: Any, topic: Optional[str] = None) -> Any:
        """
        Sends a message and waits for a response
        """
        if topic is None:
            topic = str(uuid4())
        await self.send_message(TopicMessage(topic=topic, message=message).json())
        return await self.await_response_once(topic)


ConnectionCallbackType = Callable[[TopicSocketManager], Coroutine]
DisconnectionCallbackType = Callable[[TopicSocketManager], Coroutine]

class SocketCoordinator:
    def __init__(self):
        self.connected_sockets = set()
        self.on_connect_callbacks = []
        self.on_disconnect_callbacks = []

    def add_on_connect_callback(self, callback: ConnectionCallbackType):
        self.on_connect_callbacks.append(callback)

    def remove_on_connect_callback(self, callback: ConnectionCallbackType):
        self.on_connect_callbacks.remove(callback)

    def add_on_disconnect_callback(self, callback: DisconnectionCallbackType):
        self.on_disconnect_callbacks.append(callback)

    def remove_on_disconnect_callback(self, callback: DisconnectionCallbackType):
        self.on_disconnect_callbacks.remove(callback)

    async def add_socket(self, socket):
        print('New connection')
        socket_manager = TopicSocketManager(socket)
        self.connected_sockets.add(socket_manager)
        for callback in self.on_connect_callbacks:
            callback(socket_manager)
        await socket_manager.start_listener()
        self.connected_sockets.remove(socket_manager)
        for callback in self.on_disconnect_callbacks:
            callback(socket_manager)
        print('Connection closed')
