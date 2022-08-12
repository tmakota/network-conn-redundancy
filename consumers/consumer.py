import asyncio
from time import sleep
import websockets
from websockets import ConnectionClosed
from dotenv import load_dotenv
import os
'''
The connection set has a list of all connections the client knows of. 
New connections are added/removed from here based on their status
'''
connections = set()

load_dotenv()
'''
This function creates the initial connections.
'''
async def hello():
    pingInterval = int(os.getenv('PING_INTERVAL'))
    uri = os.getenv('HOST')
    test_uri = uri + "test"
    async with websockets.connect(uri, ping_interval=pingInterval) as websocket1:
        connections.add(websocket1)
        sleep(1)
        async with websockets.connect(uri, ping_interval=pingInterval) as websocket2:
            connections.add(websocket2)
            sleep(1)
            print("Websocket1: ", websocket1.id.hex, websocket1.local_address)
            print("Websocket2: ", websocket2.id.hex, websocket2.local_address)
            await websockets.connect(test_uri)
            asyncio.gather(
                    consumerHandler(websocket1),
                    consumerHandler(websocket2), 
                )
            await checkConnStatus(uri)
            # websocket1_task = asyncio.create_task(check_conn_status(websocket1, uri))
            # websocket2_task = asyncio.create_task(check_conn_status(websocket2, uri))

'''
This is the function which keeps listening for incoming packets over the websocket. Each connection should have one listener for it.
'''
async def consumerHandler(websocket):
    async for message in websocket:
        consumer(message, websocket)
        
'''
This function is responsible for checking if all the websocket connections to the server are open. If closed, it creates a new connection to the server.
'''
async def checkConnStatus(uri):
    while True:
        for websocket in connections:
            if websocket.open == False:
                connections.remove(websocket) #remove closed connection
                websocket = await websockets.connect(uri)
                connections.add(websocket) #add new connectionto connections set and add a listener for it. 
                asyncio.gather(consumerHandler(websocket))
        await asyncio.sleep(2)
                
'''
This is the consumer processing function. Currently, it just prints the message sent to it. 
This emulates what the client of the 'SDK' will be using the data it receives. 
'''
def consumer(msg, websocket):
    print(msg, websocket.id.hex)
    return 


if __name__ == "__main__":
    asyncio.run(hello())
