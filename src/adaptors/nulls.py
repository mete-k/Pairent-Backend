import time, uuid
from typing import Protocol

class IdGen(Protocol):
    def new_id(self) -> str: ...

class Clock(Protocol):
    def now_ts(self) -> int: ...

class Uuid4Gen:
    def new_id(self) -> str:
        return str(uuid.uuid4())

class SystemClock:
    def now_ts(self) -> int:
        return int(time.time())
