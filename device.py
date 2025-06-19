import json
from typing import Literal, Dict, cast

from schemas import SetState, SetSchedule, SetMode

PinMode = Literal["manual", "auto"]
PinState = Literal[1, 0]
const_pins = [4, 5, 15, 16, 17, 18, 21, 22, 23]
pins_config = {i: {'mode': 'manual', 'state': 0} for i in const_pins}


class DeviceStateManager:
    def __init__(self):
        self.ws = None
        self.pin_modes: Dict[int, PinMode] = {}
        self.pin_status: Dict[int, PinState] = {}
        self.pin_schedule: Dict[int, Dict[str, str]] = {}

        for pin, cfg in pins_config.items():
            self.pin_modes[pin] = cast(PinMode, cfg["mode"])
            self.pin_status[pin] = cast(PinState, cfg["state"])

    async def set_ws(self, websocket):
        self.ws = websocket

    async def report_to(self, pin: int):
        if not pin:
            pin_list = []
            for pin in const_pins:
                pin_list.append(pin)
        else:
            pin_list = [pin]
        report_data = []
        for pin in pin_list:
            data = {'pin': pin,
                    'state': self.pin_status.get(pin),
                    'mode': self.pin_modes.get(pin),
                    'schedule': self.pin_schedule.get(pin)}
            report_data.append(data)
        payload = {'type': 'report', 'pin_list': report_data}
        self.ws.send(payload)

    async def set_mode(self, pin: int, mode: PinMode):
        self.pin_modes[pin] = mode
        await self.report_to(pin)

    async def set_state(self, pin: int, state: PinState):
        self.pin_status[pin] = state
        await self.report_to(pin)

    async def set_schedule(self, pin: int, on_time: str, off_time: str):
        self.pin_schedule[pin] = {"on": on_time, "off": off_time}
        await self.report_to(pin)

    async def get_report(self, pin: int = None):
        await self.report_to(pin)
