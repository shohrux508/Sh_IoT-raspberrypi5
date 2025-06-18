import json
import asyncio
import websockets
from pyee.asyncio import AsyncIOEventEmitter
from dotenv import load_dotenv
from managers import device_state as device

import os

load_dotenv('.env')
URL = os.getenv('URL')

event_bus = AsyncIOEventEmitter()

auth_token = 'abc123'

RECONNECT_DELAY = 3

gpio_state = {}  # {pin: 0 or 1}
modes = {}  # {pin: "manual" | "auto"}
schedule = {}  # {pin: {"on": ..., "off": ...}}
global ws_connection


# ------------------------------
async def websocket_client():
    global ws_connection
    while True:
        try:
            async with websockets.connect(URL) as websocket:
                print(f"[{now()}] ✅ Connected to {URL}")
                await websocket.send(json.dumps({'auth_token': auth_token}))

                while True:
                    try:
                        msg = await websocket.recv()
                        if msg == 'ping':
                            await websocket.send('pong')
                            continue

                        try:
                            data = json.loads(msg)
                        except json.JSONDecodeError:
                            print(f"[{now()}] ⚠️ Bad JSON:", msg)
                            continue

                        event_bus.emit('message_from_server', data, websocket)

                    except websockets.ConnectionClosed as e:
                        print(f"[{now()}] 🔌 Disconnected: {e}. Reconnecting in {RECONNECT_DELAY}s…")
                        break

                    await asyncio.sleep(0.01)

        except Exception as e:
            print(f"[{now()}] ❌ Connection error: {e}. Reconnecting in {RECONNECT_DELAY}s…")
            await asyncio.sleep(RECONNECT_DELAY)


# ------------------------------
@event_bus.on('message_from_server')
async def handle_message(msg, ws):
    try:
        data = json.loads(msg)
    except:
        print(f"Not JSON: {msg}")
        return
    print(f'Message from server: {data}')
    action = data.get('action')
    pin = int(data.get('pin'))
    request_id = data.get('request_id', None)
    await device.set_ws(websocket=ws)
    print(device.ws)
    # Ответ по умолчанию
    response = {
        'action': action,
        'result': 'ok',
        'request_id': request_id
    }

    if action == 'set_state':
        state = data.get('state')
        await device.set_state(pin=pin, state=int(state))
        print(f"[{now()}] ⚙️ GPIO {pin} set to {state}")

    elif action == 'set_mode':
        mode = data.get('mode')
        await device.set_mode(pin=pin, mode=mode)
        print(f"[{now()}] 🔁 Mode set for GPIO {pin}: {mode}")

    elif action == 'set_schedule':
        on = data.get('on_time')
        off = data.get('off_time')
        await device.set_schedule(pin=pin, on_time=on, off_time=off)
        print(f"[{now()}] ⏱ Schedule set for GPIO {pin}: {schedule[pin]}")

    else:
        response['result'] = 'error'
        print(f"[{now()}] ❓ Unknown action: {action}")

    await ws.send(json.dumps(response))
    print(f"[{now()}] ✅ Responded to {action} (request_id: {request_id})")


# ------------------------------
def now():
    return f"{asyncio.get_event_loop().time():.1f}"


if __name__ == "__main__":
    print("🟢 Device simulator started")
    asyncio.run(websocket_client())
