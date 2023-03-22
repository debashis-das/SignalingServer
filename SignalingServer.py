import asyncio
import json

import websockets

connections = []


async def handler(websocket):
    async for message in websocket:
        print('message :', message)
        cMessage = json.loads(message)
        peerId = cMessage['peerId']
        if cMessage['eventType'] == 'READY':
            if len(connections) != 0:
                await websocket.send(json.dumps({'eventType': 'PEER', 'connection': connections[0][0]}))
                await connections[0][1].send(json.dumps({'eventType': 'PEER', 'connection': peerId}))
            connections.append((peerId, websocket))
        elif cMessage['eventType'] == 'OFFER':
            print('OFFER :', cMessage)
            await sendMessage(peerId, message)
        elif cMessage['eventType'] == 'ANSWER':
            print('ANSWER :', cMessage)
            await sendMessage(peerId, message)
        elif cMessage['eventType'] == 'CANDIDATE':
            print('CANDIDATE :', cMessage)
            await sendMessage(peerId, message)
        else:
            print("ELSE--->")


async def sendMessage(peerId, message):
    if connections[0][0] == peerId:
        await connections[1][1].send(message)
    else:
        await connections[0][1].send(message)


# async def broadcast(message):
#     for key in connections:
#         await connections[key].send(json.dumps(message))


async def main():
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
