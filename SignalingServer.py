import asyncio
import json

import websockets

connections = dict()


async def handler(websocket):
    async for message in websocket:
        cMessage = json.loads(message)
        print(cMessage)
        if cMessage['eventType'] == 'READY':
            key = (cMessage['peerId'], cMessage['peerType'])
            if key in connections:
                error = dict()
                error['eventType'] = 'ERROR'
                error['message'] = f'{key[0]} is already connected to the Server.'
                await websocket.send(json.dumps(error))
                raise websockets.ConnectionClosedOK(sent=1001, rcvd=1000)
            else:
                await websocket.send(json.dumps({'eventType': 'INFO', 'connections': list(connections)}))
                connections[key] = websocket
                await broadcast({'eventType': 'INFO', 'connections': list(connections)})
        elif cMessage['eventType'] == 'OFFER' or cMessage['eventType'] == 'CANDIDATE':
            if cMessage['eventType'] == 'CANDIDATE' and len(cMessage['message']['candidate']) == 0:
                continue
            await broadcast(json.dumps(cMessage))
        elif cMessage['eventType'] == 'PRIVATE_MESSAGE':
            cKey = (cMessage['peerId'], cMessage['peerType'])
            if cKey in connections:
                await connections[(cMessage['peerId'], cMessage['peerType'])].send(cMessage['message'])
            else:
                await websocket.send({'eventType': 'ERROR', 'message': f'target{cMessage["peerId"]} is not found'})
        elif cMessage['eventType'] == 'DISCONNECT':
            key = (cMessage['peerId'], cMessage['peerType'])
            connections.pop(key)
            await broadcast({'eventType': 'INFO', 'connections': list(connections),
                             'message': f'target{cMessage["peerId"]} is disconnected'})
        else:
            print("ELSE--->")


async def broadcast(message):
    for key in connections:
        await connections[key].send(json.dumps(message))


async def main():
    async with websockets.serve(handler, "192.168.", 8765):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
