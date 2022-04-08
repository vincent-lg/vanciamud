# Copyright 2022, LE GOFF Vincent
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Interactive console to execute arbitrary Python code."""


from code import InteractiveConsole
import sys


class Shell(InteractiveConsole):

    """Slight modification of the interactive console for TalisMUD."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.output = ""

    def write(self, data):
        """Write stdout/stderr data."""
        self.output += data

    def push(self, code):
        """Push the code."""
        write = sys.stdout.write
        self.output = ""
        sys.stdout.write = self.write
        more = super().push(code)
        sys.stdout.write = write
        return more
