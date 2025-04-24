import asyncio
import websockets

async def websocket_client():
    uri = "wss://shiot-production.up.railway.app/devices/register/3"
    async with websockets.connect(uri) as websocket:
        print("Connected to server.")
        while True:
            try:
                msg = await websocket.recv()
                print(f"Received: {msg}")
                if msg == 'ping':
                    await websocket.send('pong')
                    print("Sent: pong")
            except websockets.ConnectionClosed:
                print("Connection closed by server.")
                break
            await asyncio.sleep(0.01)

if __name__ == "__main__":
    print("Client started…")
    asyncio.run(websocket_client())
