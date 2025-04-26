import asyncio
import time

import websockets

from helpers import filter_data


class manageArduino:
    def __init__(self, **pins):
        self.pins = pins
        self.pins_status = {f"{key}": 0 for key, value in pins.items()}
        self.pins_in_num = {int(key.replace('pin', '')): f"{key}" for key, value in pins.items()}

    def get_pin(self, pin: int):
        return self.pins_in_num.get(pin)

    def get_status(self, pin: int):
        return self.pins_status[self.get_pin(pin)]

    def toggle(self, pin: int = None):
        self.pins_status[self.get_pin(pin)] = int(not self.get_status(pin))
        print(self.pins_status)
        return self.get_status(pin)

    def set_pin(self, pin: int, status: int):
        self.pins_status[self.get_pin(pin)] = status
        return status


arduino = manageArduino(pin2='led1', pin3='led2', pin4='led3')
arduino.set_pin(pin=2, status=1)
print(arduino.pins_status)


async def websocket_client():
    uri = "wss://shiot-production.up.railway.app/devices/register/3"
    async with websockets.connect(uri) as websocket:
        print("Connected to server.")
        while True:
            try:
                msg = await websocket.recv()
                # print(f"Received: {msg}")
                if msg == 'ping':
                    await websocket.send('pong')
                    # print("Sent: pong")
                if msg.startswith('set_pin:'):
                    # set_pin:5-1
                    pin, status = (filter_data('set_pin:')).split('-')
                    arduino.set_pin(pin, status)
                if msg.startswith('toggle_pin:'):
                    pin = int(filter_data(msg, 'toggle_pin:'))
                    arduino.toggle(pin=pin)




            except websockets.ConnectionClosed:
                print("Connection closed by server.")
                break
            await asyncio.sleep(0.01)


if __name__ == "__main__":
    print("Client started…")
    asyncio.run(websocket_client())
