import asyncio
import time

import websockets

from helpers import filter_data


class manageArduino:
    def __init__(self, **pins):
        self.pins = pins
        self.pins_status = {key: 0 for key, value in pins.items()}
        self.pins_in_num = {int(key.replace('pin', '')): key for key, value in pins.items()}

    def get_pin(self, pin: int):
        pin_name = self.pins_in_num.get(pin)
        if pin_name is None:
            print(f"[Предупреждение] Пин {pin} не найден.")
            return None
        return pin_name

    def get_status(self, pin: int):
        key = self.get_pin(pin)
        if key is None:
            return None
        return self.pins_status.get(key)

    def toggle(self, pin: int = None):
        if pin is None:
            for key, value in self.pins_status.items():
                self.pins_status[key] = int(not value)
        else:
            key = self.get_pin(pin)
            if key is not None:
                self.pins_status[key] = int(not self.pins_status[key])
        return self.get_status(pin) if pin else None

    def set_pin(self, pin: int, status: bool):
        key = self.get_pin(pin)
        if key is not None:
            self.pins_status[key] = int(status)
        return self.get_status(pin)



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
                if msg == 'ping':
                    await websocket.send('pong')
                else:
                    print(f"Получено: {msg}")
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
