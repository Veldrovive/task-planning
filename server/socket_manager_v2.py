import asyncio
from typing import Callable, Any, Coroutine, Optional
from models import TopicMessage
from uuid import uuid4

from simple_websocket_server import WebSocket

TopicCallbackType = Callable[[str, Any], Coroutine]

class MultiThreadTopicSocketManager(WebSocket):
    def __init__(self, server, sock, address):
        super().__init__(server, sock, address)
        self.topic_callbacks = {}
        self.message_queue = {}
        self.on_disconnect_callbacks = []

    def add_topic_callback(self, topic: str, callback: TopicCallbackType):
        self.topic_callbacks[topic] = callback

    def remove_topic_callback(self, topic: str):
        del self.topic_callbacks[topic]

    def add_on_disconnect_callback(self, callback: Callable):
        self.on_disconnect_callbacks.append(callback)

    def handle_close(self):
        print('Socket closed', self.address)
        for callback in self.on_disconnect_callbacks:
            callback(self)

    def handle(self):
        if self.data == "ping":
            self.send_message("pong")
            return
        # Then self.data is a topic message
        try:
            message = TopicMessage.parse_raw(self.data)
            # print('Have handlers for topics:', list(self.topic_callbacks.keys()))
        except Exception as e:
            print('Error when parsing topic message', e)
            return
        if message.topic in self.topic_callbacks:
            try:
                if message.topic not in self.message_queue:
                    self.message_queue[message.topic] = []
                self.message_queue[message.topic].append(message.message)
            except Exception as e:
                print('Error when adding message to message queue', message.topic, message.message)
                print(e)

    async def handle_callbacks(self):
        """
        Calls the callbacks foe every message in the message_queue
        """
        messages = list(self.message_queue.items())
        for topic, messages in messages:
            # print("Handling", len(messages), "messages for topic", topic)
            for message in messages:
                if topic in self.topic_callbacks:
                    asyncio.ensure_future(self.topic_callbacks[topic](topic, message))
                # Remove the message from the queue
                self.message_queue[topic].remove(message)
                # If there are no more messages for the topic, remove the topic
                if len(self.message_queue[topic]) == 0:
                    del self.message_queue[topic]

    def send(self, message: Any, topic: str):
        """
        Sends a message as a topic
        """
        self.send_message(TopicMessage(topic=topic, message=message).json())

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

    async def send_and_await_response(self, message: Any, topic: Optional[str] = None) -> Any:
        """
        Sends a message and waits for a response
        """
        if topic is None:
            topic = str(uuid4())
        self.send(message, topic)
        return await self.await_response_once(topic)



class TopicSocketManager(WebSocket):
    def __init__(self, server, sock, address):
        super().__init__(server, sock, address)
        self.topic_callbacks = {}

    def add_topic_callback(self, topic: str, callback: TopicCallbackType):
        self.topic_callbacks[topic] = callback

    def remove_topic_callback(self, topic: str):
        del self.topic_callbacks[topic]

    def handle(self):
        if self.data == "ping":
            self.send_message("pong")
            return
        # Then self.data is a topic message
        message = TopicMessage.parse_raw(self.data)
        print('Got topic message', message.topic, message.message)
        # print('Have handlers for topics:', list(self.topic_callbacks.keys()))
        if message.topic in self.topic_callbacks:
            try:
                asyncio.ensure_future(self.topic_callbacks[message.topic](message.topic, message.message))
            except Exception as e:
                print('Error in topic callback while handling topic message', message.topic, e)

    def connected(self):
        print(self.address, 'connected')

    def handle_close(self):
        print(self.address, 'closed')

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
        self.send_message(TopicMessage(topic=topic, message=message).json())

    async def send_and_await_response(self, message: Any, topic: Optional[str] = None) -> Any:
        """
        Sends a message and waits for a response
        """
        if topic is None:
            topic = str(uuid4())
        self.send_message(TopicMessage(topic=topic, message=message).json())
        return await self.await_response_once(topic)