import asyncio
from time import sleep
import websockets
from websockets.exceptions import ConnectionClosed
from dotenv import load_dotenv
import os
load_dotenv()

'''
The connection dictionary has a list of all connections for a given client.
It helps manage multiple connections from a single client
'''
connections = {}

class AllConnectionsClosedError(Exception):
    """Raised when all connections in a connection pair/set are closed."""
    pass



'''
Function to send data using multiple connections. 
'''
async def send(connId, msg):
    connPair = connections[connId]
    for conn in connPair:
        print("Sending", msg, "using", conn.id.hex, "status:",conn.open)
        if conn.open == True:
            await conn.send(msg)

'''
Function to keep a check for all the open connections in all connections
'''
async def connectionChecker():
    while True:
        for connectionId, connectionArray in list(connections.items()):
            #for each connection pair, check if all the connections are open.
            for conn in connections[connectionId]:
                if conn.open == False:
                    #close the connection and remove it from the pool. 
                    print("Removing connection")
                    connections[connectionId].remove(conn)
                    if len(connections[connectionId]) == 0:
                        #all connections are closed, remove connections from dict as client is supposed to re-establish the connections. 
                        del connections[connectionId]
        await asyncio.sleep(2)            
                    



'''
The make_connPair funciton is responsible for grouping the connections into pairs based on where the requests originate from
'''
def makeConnPair(websocket):
    connId = websocket.id.hex 
    if connections == {}:
        connections[connId] = []
        connections[connId].append(websocket)

    else:
        found = False

        for conn in connections:
            for ws in connections[conn]:
                if ws.remote_address[0] == websocket.remote_address[0]: 
                    found = True
                    connections[conn].append(websocket)
                    connId = conn
                    break

        if found == False:
            connId = websocket.id.hex
            connections[connId] = []
            connections[connId].append(websocket)
        
    return connId

'''
When the producer/server wants to send messages to the clients, it can use this function to look up which connections it has to use for sending the messages.
'''
def findConnPair(websocket):
    for conn in connections:
        if connections[conn][0].remote_address[0] == websocket.remote_address[0]:
            return conn
    return "None"

'''
This function keeps the connections open.
'''
async def msgReceiver(websocket):
    async for message in websocket:
        print(message)

'''
A testhandler which mimics server sending data over when it has some.
'''
async def testHandler(connId):
    i = 0 
    try:
        while True:
            msg = "Hi!" + str(i) 
            await send(connId, msg)
            await asyncio.sleep(4)
            i = i + 1
    except AllConnectionsClosedError:
        #close all connections related to connId
        connPair = connections[conn]
        for conn in connPair:
            await conn.close()
        del connections[conn]
        print("All connections related to", conn, "closed.")

'''
The main function which accepts incoming client connections and routes them to the correct handler function.
'''
async def hello(websocket):
    if websocket.path == '/':
        conn = makeConnPair(websocket)
        await msgReceiver(websocket)
    elif websocket.path == "/test":
        connId = findConnPair(websocket)
        if connId != "None":
            await testHandler(connId)
            # await websocket.close()


    
async def main():
    host = os.getenv('HOST')
    pingInterval = os.getenv('PING_INTERVAL')
    port = os.getenv('PORT')
    async with websockets.serve(hello, host, port, ping_interval=int(pingInterval)):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
