import json

import websockets
import asyncio
from pyee.asyncio import AsyncIOEventEmitter

event_bus = AsyncIOEventEmitter()
local_url = 'ws://127.0.0.1:8000/devices/ws/3/connect'
pub_url = "wss://shiot-production.up.railway.app/devices/ws/3/connect"


async def websocket_client():
    uri = pub_url
    async with websockets.connect(uri) as websocket:
        print("Connected to server.")
        data = {'auth_token': 'abc12345'}

        await websocket.send(json.dumps(data))
        while True:
            try:
                msg = await websocket.recv()
                if msg == 'ping':
                    await websocket.send('pong')
                else:
                    try:
                        data = json.loads(msg)
                    except json.JSONDecodeError:
                        print(msg)
                        continue
                    event_bus.emit('message_from_server', data, websocket)

            except websockets.ConnectionClosed:
                print("Connection closed by server.")
                break
            await asyncio.sleep(0.01)


@event_bus.on('message_from_server')
async def handle_message(msg, ws):
    request_id = msg.get('request_id', None)
    action = msg.get('action', None)
    data = {'action': action, 'status': 'done', 'request_id': request_id}
    await ws.send(json.dumps(data))


if __name__ == "__main__":
    print("Client started…")
    asyncio.run(websocket_client())
