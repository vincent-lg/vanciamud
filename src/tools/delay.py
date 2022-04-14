# Copyright (c) 2022, LE GOFF Vincent
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
# OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.


"""Tool to create delays.

This tools is used to create delays, asynchronous pauses
between actions.  Usually, users don't have to use this
tool manually, helper methods are provided (see the `call_in`
method on commands or contexts, for instance).

Delays have the ability to be persistent, that is, they require
a callback to be executed.

```python
from tools import delay
delay.schedule(5, print, "After five seconds")
# This will call print("After 5 seconds") 5 seconds later.
# Even if a full shutdown happens.
# If the game is off when the schedule should happen, it will occur
# when the game is back up, even later.
```

"""

import asyncio
from datetime import datetime, timedelta
from inspect import iscoroutine
from itertools import count
import pickle
from typing import Any, Callable, Dict, Sequence

from logbook import FileHandler, Logger

from data.delay import Delay as DbDelay

# Logger
logger = Logger()
file_handler = FileHandler(
    "logs/delays.log", encoding="utf-8", level="DEBUG", delay=True
)
file_handler.format_string = (
    "{record.time:%Y-%m-%d %H:%M:%S.%f%z} [{record.level_name}] "
    "{record.message}"
)
logger.handlers.append(file_handler)


class Delay:

    """Class to store delays, and persist them if necessary.

    When a delay is created, an asynchronous task is created
    to execute it.  Should the game be stopped, this delay will
    be stored in the database (see `data.delay`) which will restore
    and schedule a task again when the game is up and running once more.

    Delays are just callable that can be pickled, which includes
    top-level functions and instance methods.

    """

    _delays = {}
    _current_id = count(1)
    _game_service = None

    def __init__(
        self,
        id: int,
        expire_at: timedelta,
        callback: Callable,
        args: Sequence[Any],
        kwargs: Dict[str, Any],
    ):
        self.id = id
        self.expire_at = expire_at
        self.callback = callback
        self.args = args
        self.kwargs = kwargs
        self.persistent = None
        type(self)._delays[self.id] = self

    def __repr__(self):
        arguments = ", ".join(str(arg) for arg in self.args)
        arguments += ", ".join(
            f"{key}={value}" for key, value in self.kwargs.items()
        )
        return f"<Delay {self.id} {self.callback}({arguments})"

    def _schedule(self):
        seconds = (self.expire_at - datetime.utcnow()).total_seconds()
        seconds = 0 if seconds < 0 else seconds
        loop = asyncio.get_event_loop()
        loop.call_later(seconds, type(self)._game_service.call_delay, self)
        logger.debug(f"Preparing to call {self!r} in {seconds} seconds")

    def _execute(self):
        """Prepare to execute."""
        try:
            result = self.callback(*self.args, **self.kwargs)
        except Exception:
            logger.exception("An error occurred while executing {self!r}")
        else:
            if iscoroutine(result):
                # Schedule it asynchronously
                loop = asyncio.get_event_loop()
                loop.create_task(self._async_execute(result))
            else:
                type(self)._delays.pop(self.id, None)
                if self.persistent is not None:
                    type(self.persistent).repository.delete(self.persistent)

    async def _async_execute(self, coroutine):
        """Execute the delayed action."""
        try:
            await coroutine
        except Exception:
            logger.exception("An error occurred while executing {self!r}")
        finally:
            type(self)._delays.pop(self.id, None)
            if self.persistent is not None:
                self.persistent.repository.delete(self.persistent)

    @classmethod
    def schedule(cls, *args, **kwargs):
        """Schedule a callback for later.

        Args:
            delay (int or timedelta): the delay, specified either
                    as seconds or a `datetime.timedelta`.
            callback (callable): the callback to call.
            Any additional position argument will be sent to the callback.

        Likewise, keyword arguments will be sent to the callback as well.

        Raises:
            ValueError: the callback cannot be pickled and persisted
            in the database.

        """
        if (length := len(args)) < 2:
            if length == 0:
                raise ValueError("missing argument: delay in seconds")
            elif length == 1:
                raise ValueError("missing argument: callback to call")

        # Get the delay and callback from *args.
        args = list(args)
        delay = args.pop(0)
        callback = args.pop(0)

        # Check the time.
        expire_at = datetime.utcnow()
        if isinstance(delay, (int, float)):
            expire_at += timedelta(seconds=delay)
        elif isinstance(delay, timedelta):
            expire_at += delay
        else:
            raise ValueError(f"invalid delay: {delay!r}")

        # Check that the callable can be pickled.
        args = tuple(args)
        try:
            cls._pickled(callback, args, kwargs)
        except TypeError:
            raise ValueError("cannot pickle this callback")

        # Create and return a delay.
        id = next(cls._current_id)
        obj = cls(id, expire_at, callback, args, kwargs)
        obj._schedule()
        return obj

    @classmethod
    def _pickled(cls, callback, args, kwargs):
        return pickle.dumps((callback, args, kwargs))

    @classmethod
    def persist(cls):
        """Persist all non-persistent delays."""
        for id, delay in cls._delays.items():
            if delay.persistent is None:
                pickled = cls._pickled(
                    delay.callback, delay.args, delay.kwargs
                )
                DbDelay.repository.create(
                    expire_at=delay.expire_at, pickled=pickled
                )
                logger.debug(f"Persisting {delay!r} in the database.")
