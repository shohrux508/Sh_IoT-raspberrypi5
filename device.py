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

    async def report_to(self, data):
        pass

    async def set_mode(self, pin: int, mode: PinMode):
        self.pin_modes[pin] = mode
        data = SetMode(pin=pin, mode=mode).model_dump()
        await self.report_to(data)

    async def set_state(self, pin: int, state: PinState):
        self.pin_status[pin] = state
        data = SetState(pin=pin, state=state).model_dump()
        await self.report_to(data)

    async def set_schedule(self, pin: int, on_time: str, off_time: str):
        self.pin_schedule[pin] = {"on": on_time, "off": off_time}
        data = SetSchedule(pin=pin, on_time=on_time, off_time=off_time).model_dump()
        await self.report_to(data)

    async def get_mode(self, pin: int):
        pin_mode = self.pin_modes.get(pin, "manual")
        data = {'pin': pin, 'mode': pin_mode}
        await self.report_to(data)

    async def get_status(self, pin: int):
        pin_state = self.pin_status.get(pin, 0)
        data = {'pin': pin, 'state': pin_state}
        await self.report_to(data)

    async def get_schedule(self, pin: int):
        pin_schedule = self.pin_schedule.get(pin, {})
        on = pin_schedule.get('on_time')
        off = pin_schedule.get('off_time')
        data = {'pin': pin, 'on_time': on, 'off_time': off}
        await self.report_to(data)
