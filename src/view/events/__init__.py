from enum import Enum, auto
from typing import Callable

class Event(Enum):
    LOAD_APP = auto()

_event_subscriptors: dict[Event, [Callable]] = {}


def event_connect(event: Event, func: Callable):
    if event not in _event_subscriptors:
        _event_subscriptors[event] = []
    _event_subscriptors[event].append(func)

def event_emit(event: Event, *args, **kwargs):
    for func in _event_subscriptors[event]:
        func(*args, **kwargs)
