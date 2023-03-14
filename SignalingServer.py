import asyncio
import json

import websockets

connections = dict()


async def handler(websocket):
    try:
        async for message in websocket:
            c_message = json.loads(message)
            if c_message['event-type'] == 'READY':
                key = (c_message['peerId'], c_message['peerType'])
                if key in connections:
                    error = dict()
                    error['event-type'] = 'ERROR'
                    error['message'] = f'{key[0]} is already connected to the Server.'
                else:
                    connections.append(key)

            await websocket.send(message)
    except websockets.ConnectionClosedOK:
        print(websocket)


async def main():
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
