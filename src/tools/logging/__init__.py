# Copyright (c) 2023, LE GOFF Vincent
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

"""Package containing a simple logging system.

Loggers, handlers and formatters are defined in sub-modules.

Simple usage:

```python
from tools.login import Logger

class AppLogger(Logger):

    '''A logger specific to this app, already configured.'''

    def config(self, name):
        '''Configure this logger.'''
        self.options["directory"] = "logs"
        self.handlers.append(Handler.STREAM, sys.stdout, level=Level.INFO)
        self.handlers.append(Handler.FILE, f"{name}.log", level=LEVEL.DEBUG)

logger = AppLogger("test")
# Writing in the logger will write in a "logs/test.log" file all messages,
# but will only display the messages at or above INFO.
logger.debug("A debug message") # no print
logger.info("An informative message") # print to stdout
# you can also use `logger.warn` instead of `ogger.warning`
logger.warning("A warning message") # print to stdout
logger.error("An error message") # print to stdout
# In a try/except case, you can use `logger.exception` which will log
# a full traceback below the message:
try:
    1 / 0
except Exception:
    logger.exception("Something went wrong:")

Individual handlers can be configured in `add_handler` (see `Logger.config`).

"""

from tools.logging.batch import Day, Hour  # noqa: F401
from tools.logging.handler import File, Stream  # noqa: F401
from tools.logging.level import Level  # noqa: F401
from tools.logging.logger import Logger  # noqa: F401
