import json
import asyncio
import websockets
from pyee.asyncio import AsyncIOEventEmitter

event_bus = AsyncIOEventEmitter()

auth_token = 'abc123'

local_url = f'ws://127.0.0.1:8000/devices/ws/1/connect'
pub_url = "wss://shiotstandard-production.up.railway.app/devices/ws/1/connect"

RECONNECT_DELAY = 3
uri = pub_url

gpio_state = {}  # {pin: 0 or 1}
modes = {}  # {pin: "manual" | "auto"}
schedule = {}  # {pin: {"on": ..., "off": ...}}


# ------------------------------
async def websocket_client():
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                print(f"[{now()}] ✅ Connected to {uri}")
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
    action = msg.get('action')
    pin = msg.get('pin')
    request_id = msg.get('request_id', None)

    # Ответ по умолчанию
    response = {
        'action': action,
        'result': 'ok',
        'request_id': request_id
    }

    if action == 'set_gpio':
        state = msg.get('state')
        gpio_state[pin] = state
        print(f"[{now()}] ⚙️ GPIO {pin} set to {state}")

    elif action == 'set_mode':
        mode = msg.get('mode')
        modes[pin] = mode
        print(f"[{now()}] 🔁 Mode set for GPIO {pin}: {mode}")

    elif action == 'set_schedule':
        schedule[pin] = {
            "on": msg.get("on_time"),
            "off": msg.get("off_time")
        }
        print(f"[{now()}] ⏱ Schedule set for GPIO {pin}: {schedule[pin]}")

    else:
        response['status'] = 'unknown_action'
        print(f"[{now()}] ❓ Unknown action: {action}")

    await ws.send(json.dumps(response))
    print(f"[{now()}] ✅ Responded to {action} (request_id: {request_id})")


# ------------------------------
def now():
    return f"{asyncio.get_event_loop().time():.1f}"


if __name__ == "__main__":
    print("🟢 Device simulator started")
    asyncio.run(websocket_client())
