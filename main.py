import asyncio
import websockets
import json

async def websocket_client():
    uri = "wss://shiot-production.up.railway.app/devices/3"
    async with websockets.connect(uri) as websocket:
        while True:
            await websocket.send(json.dumps({"token":"2645"}))
            try:
                msg = await websocket.recv()
            except websockets.ConnectionClosed:
                print("WebSocket закрыт, выходим из цикла")
                break
            if msg == 'ping':
                await websocket.send('pong')
            await asyncio.sleep(0.01)

if __name__ == "__main__":
    print("Client started…")
    asyncio.run(websocket_client())

