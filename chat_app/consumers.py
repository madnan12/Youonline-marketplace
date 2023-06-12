

from channels.consumer import SyncConsumer, AsyncConsumer

class ChatConsumer(SyncConsumer):


    # This Method/Handler triggered when connection Open between client and server
    def websocket_connect(self, event): # Rank 1
        print('Connection Stablished! user Online')


    # This method/handler trigged when server received Data from cleint side
    def websocket_receive(self, event): # Rank 2
        print('Client message Received')


    # This handler triggered when Connection closed between Client and Server 
    def websocket_disconnect(self, event): #  Rank 3
        print('Connection Closed')



class ChatRealTimeConsumer(AsyncConsumer):

    
    # This Method/Handler triggered when connection Open between client and server
    async def websocket_connect(self, event): # Rank 1
        print('Connection Stablished! user Online')


    # This method/handler trigged when server received Data from cleint side
    async def websocket_receive(self, event): # Rank 2
        print('Client message Received')


    # This handler triggered when Connection closed between Client and Server 
    async def websocket_disconnect(self, event): #  Rank 3
        print('Connection Closed')