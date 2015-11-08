from ws4redis.publisher import RedisPublisher
from ws4redis.redis_store import RedisMessage
from ws4redis.subscriber import RedisSubscriber as RS

class RedisSubscriber(RS):

    def send_persited_messages(self, websocket):
        for channel in self._subscription.channels:
            message = self._connection.get(channel)
            if message:
                print message
                websocket.send(message)
