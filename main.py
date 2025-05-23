import json
import asyncio
import websockets
from pyee.asyncio import AsyncIOEventEmitter

event_bus = AsyncIOEventEmitter()
local_url = 'ws://127.0.0.1:8000/devices/ws/3/connect'
pub_url = "wss://shiot-production.up.railway.app/devices/ws/3/connect"

RECONNECT_DELAY = 3  # секунды до повторной попытки

async def websocket_client():
    uri = pub_url
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                print(f"[{asyncio.get_event_loop().time():.1f}] Connected to {uri}")
                # отправляем аутентификацию
                await websocket.send(json.dumps({'auth_token': 'abc12345'}))

                while True:
                    try:
                        msg = await websocket.recv()
                        if msg == 'ping':
                            await websocket.send('pong')
                        else:
                            try:
                                data = json.loads(msg)
                            except json.JSONDecodeError:
                                print(f"[{asyncio.get_event_loop().time():.1f}] Bad JSON:", msg)
                                continue
                            event_bus.emit('message_from_server', data, websocket)

                    except websockets.ConnectionClosed as e:
                        print(f"[{asyncio.get_event_loop().time():.1f}] Connection closed: {e}. Reconnecting in {RECONNECT_DELAY}s…")
                        break

                    await asyncio.sleep(0.01)

        except (OSError, websockets.InvalidURI, websockets.InvalidHandshake) as e:
            print(f"[{asyncio.get_event_loop().time():.1f}] Connection error: {e}. Reconnecting in {RECONNECT_DELAY}s…")
        await asyncio.sleep(RECONNECT_DELAY)


@event_bus.on('message_from_server')
async def handle_message(msg, ws):
    request_id = msg.get('request_id')
    action = msg.get('action')
    reply = {'action': action, 'status': 'done', 'request_id': request_id}
    await ws.send(json.dumps(reply))
    print(f"[{asyncio.get_event_loop().time():.1f}] Replied to {request_id} → {action}")

if __name__ == "__main__":
    print("Client started…")
    asyncio.run(websocket_client())
