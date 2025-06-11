from pydantic import BaseModel, model_validator, field_validator


class SetState(BaseModel):
    action: str = 'set_state'
    pin: int
    state: int

    @model_validator(mode="before")
    def convert_state(cls, data):
        # data — dict с исходными данными
        state = data.get('state')
        if isinstance(state, int):
            data['state'] = 'turn_on' if state == 1 else 'turn_off'
        return data


class SetMode(BaseModel):
    action: str = 'set_mode'
    pin: int
    mode: str

    @field_validator('mode')
    def check_mode(cls, v):
        if v not in ('manual', 'auto'):
            raise ValueError("mode must be: 'manual' or 'auto'")


class SetSchedule(BaseModel):
    action: str = 'set_schedule'
    pin: int
    on_time: str
    off_time: str