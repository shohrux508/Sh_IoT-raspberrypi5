import asyncio
import websockets
from manager import Ports

async def websocket_client():
    uri = "ws://127.0.0.1:8000/devices/1"
    arduino = Ports(port_name='COM14', baud_rate=9600)
    async with websockets.connect(uri) as websocket:
        while True:
            cmd = await arduino.read_commands()
            if cmd:
                await websocket.send(cmd)
                print(f"→ Sent to WS: {cmd!r}")
            try:
                msg = await websocket.recv()
            except websockets.ConnectionClosed:
                print("WebSocket закрыт, выходим из цикла")
                break
            print(f"← Received from WS: {msg!r}")
            await arduino.send_command(msg)
            await asyncio.sleep(0.01)

if __name__ == "__main__":
    print("Client started…")
    asyncio.run(websocket_client())

