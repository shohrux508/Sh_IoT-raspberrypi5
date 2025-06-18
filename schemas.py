from pydantic import BaseModel, model_validator, field_validator


class SetState(BaseModel):
    action: str = 'set_state'
    pin: int
    state: int


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
