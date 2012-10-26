###############################################################################
#
# Copyright 2012 Stendec <me@stendec.me>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
###############################################################################
"""
This module performs conversions between Python values and packed binary data
suitable to be sent over a network connection. It functions in many ways
identically to the standard library module :module:`struct`. However, it uses
network byte order by default, and has support for variable-length strings.
"""

###############################################################################
# Imports
###############################################################################

from __future__ import unicode_literals

from struct import Struct as _Struct, error, calcsize as _calcsize


###############################################################################
# Exports and Constants
###############################################################################

__all__ = (
    "NetStruct",

    "pack", "unpack", "iter_unpack",
    "minimum_size", "initial_size"
)

bytes = type(b"")

###############################################################################
# NetStruct Class
###############################################################################

class NetStruct(object):
    """
    Return a new NetStruct object which writes and reads binary data according
    to the format string *format*. It's more efficient, as it is with
    :class:`struct.Struct`, to create a NetStruct object once and call its
    methods rather than calling the :module:`netstruct` functions with the
    same format, as the format only has to be compiled once.

    The NetStruct object works as similarly to :class:`struct.Struct` as is
    possible, with two differences.

    When using a NetStruct, the byte order defaults to network byte order
    (big-endian). This ensures, among other things, that the generated strings
    won't have any padding bytes.

    Additionally, the NetStruct supports the formatting character ``$``, which
    signifies a variable-length string. When the ``$`` is encountered during
    unpacking, the most recently unpacked value will be used as the string's
    length. Attempting to unpack a non-numeric value, such as ``?`` (bool),
    will raise a :class:`struct.error`. As an example of unpacking::

        >>> netstruct.unpack("b$", "\x0cHello World!")
        ['Hello World!']

    When the ``$`` is encountered during packing, the string length will be
    used for the value directly before the string. Example::

        >>> netstruct.pack("b$", "Hello World!")
        '\x0cHello World!'
    """

    __slots__ = ("_format", "_pairs", "_minsize", "_initsize")

    def __init__(self, format):
        self._format = format

        if not format:
            self._pairs = []
            self._minsize = 0
            self._initsize = 0
        elif not isinstance(format, bytes):
            raise TypeError("NetStruct() format must be a byte string.")
        else:
            # Make sure there aren't any back-to-back strings and/or arrays.
            if b"$$" in format:
                raise error("invalid sequence in netstruct format")

            # Break the format down.
            self._pairs = pairs = []
            self._minsize = 0

            if format[:1] in b"@=<>!":
                byte_order = format[:1]
                format = format[1:]
            else:
                byte_order = b"!"

            while format:
                segment, sep, format = format.partition(b"$")

                if sep and (not segment or not segment[-1:] in "bBhHiIlLqQP"):
                    raise error("bad char in struct format")

                st = _Struct(byte_order + segment)
                self._minsize += st.size
                pairs.append((st, _count(segment), sep))

            self._initsize = pairs[0][0].size

    @property
    def format(self):
        """ The format string used to construct this NetStruct. """
        return self._format

    @property
    def minimum_size(self):
        """ The minimum possible size of this NetStruct. """
        return self._minsize

    @property
    def initial_size(self):
        """
        The size of this NetStruct up to the first
        variable-length string.
        """
        return self._initsize

    ##### Methods #############################################################

    def pack(self, *data):
        """
        Return a string containing the values *data packed according to this
        NetStruct's format.
        """
        result = []
        append = result.append

        for struct, count, has_string in self._pairs:
            if has_string:
                append(struct.pack(*data[:count-1] +
                                           (len(data[count-1]),)))
                append(data[count-1])
            else:
                append(struct.pack(*data[:count]))
            data = data[count:]

        return b"".join(result)

    def unpack(self, data):
        """
        Unpack the string according to this NetStruct's format.
        """
        out = self.iter_unpack(data).next()
        if isinstance(out, (int,long)):
            raise error("unpack requires a string argument of length %d" % (len(data) + out))
        return out

    def iter_unpack(self, data=b""):
        """
        Unpack the string according to this NetStruct's format.

        Because the length of the string needed to unpack a NetStruct with a
        variable length string is unknown, this method returns an iterator,
        able to request additional data until it is able to unpack the entire
        message.

        When using the iterator, calls to .next() and .send() will return
        either the number of bytes needed to finish unpacking, or a list with
        the completed value. As such, the following is an example of how you
        might use this::

            >>> ns = NetStruct(b"ih$5b")
            >>> it = ns.iter_unpack()
            >>> it.next()
            6
            >>> it.send(b"\x12\x05\x00\x00\x0B\x00")
            11
            >>> it.send(b"largeBiomes")
            5
            >>> it.send(b"\x00\x00\x01\x00\x08")
            [1298, "largeBiomes", 0, 0, 1, 0, 8]

        You may also provide an initial string to start the process. Be aware
        that, if you provide a long enough string, the first call to .next() or
        .send() may return the completed value.

        Once the completed value is returned, you may make one last call to
        .next() or .send() to retrieve any unconsumed data.
        """
        result = []

        for struct, count, has_string in self._pairs:

            needed = struct.size
            while needed > len(data):
                new_data = yield needed - len(data)
                if new_data:
                    data += new_data

            result.extend(struct.unpack(data[:needed]))
            data = data[needed:]

            if has_string:
                needed = result.pop()
                while needed > len(data):
                    new_data = yield needed - len(data)
                    if new_data:
                        data += new_data

                result.append(data[:needed])
                data = data[needed:]

        yield result
        yield data

###############################################################################
# Private Methods
###############################################################################

def _count(format):
    """
    Count the number of variables needed to pack a given format.
    """
    if format[:1] in b"@=<>!":
        format = format[1:]

    count = 0
    q = b""

    for char in format:
        if char.isdigit():
            q += char
            continue
        elif char in b" \t\r\n":
            if q:
                raise error("bad char in struct format")
            continue
        elif char in b"ps":
            count += 1
            q = b""
        elif char in b"xcbB?hHiIlLqQfdP":
            count += int(q or 1)
            q = b""
        else:
            raise error("bad char in struct format")

    return count


###############################################################################
# Public Methods
###############################################################################

def pack(format, *data):
    """
    Return a string containing the values *data packed according to the
    given format.
    """
    return NetStruct(format).pack(*data)

def unpack(format, data):
    """
    Unpack the string packed according to the given format.
    """
    return NetStruct(format).unpack(data)

def iter_unpack(format, initial=b""):
    """
    Unpack the string according to the given format.
    See :meth:`NetStruct.iter_unpack` for more details.
    """
    return NetStruct(format).iter_unpack(initial)

def minimum_size(format):
    """
    Return the minimum possible size of the given packed data format.
    """
    if not format[:1] in b"@=<>!":
        format = b"!" + format

    return _calcsize(format.replace(b"$", b""))

def initial_size(format):
    """
    Return the size of the given packed data format up to the first
    variable-length string.
    """
    if format[:1] in b"@=<>!":
        byte_order = format[:1]
        format = format[1:]
    else:
        byte_order = b"!"

    index = format.find(b"$")
    if not index:
        return 0
    elif index > 0:
        if b"$$" in format:
            raise error("invalid sequence in netstruct format")
        format = format[:index]
    return _calcsize(byte_order + format)
