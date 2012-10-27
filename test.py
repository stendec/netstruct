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

###############################################################################
# Imports
###############################################################################

from __future__ import unicode_literals

import netstruct
import unittest

###############################################################################
# Tests
###############################################################################

class TestConstruction(unittest.TestCase):
    def test_empty(self):
        netstruct.NetStruct(b"")

    def test_unicode(self):
        with self.assertRaises(TypeError):
            netstruct.NetStruct("ib")

    def test_other_type(self):
        with self.assertRaises(TypeError):
            netstruct.NetStruct(42)

    def test_adjacent_strings(self):
        with self.assertRaises(netstruct.error):
            netstruct.NetStruct(b"b$$")

    def test_immediate_string(self):
        with self.assertRaises(netstruct.error):
            netstruct.NetStruct(b"$")

    def test_quantity_string(self):
        with self.assertRaises(netstruct.error):
            netstruct.NetStruct(b"i5$")

    def test_parsing(self):
        ns = netstruct.NetStruct(b"ih$5b")

        self.assertEqual(len(ns._pairs), 2)
        self.assertEqual(ns.minimum_size, 11)
        self.assertEqual(ns.initial_size, 6)
        self.assertEqual(ns.count, 7)

class TestUnpack(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(netstruct.unpack(b"", b""), [])

    def test_not_enough(self):
        with self.assertRaises(netstruct.error):
            netstruct.unpack(b"4i", b"\x00\x01\x02\x03")

    def test_too_much(self):
        self.assertEqual(
            netstruct.unpack(b"i", b"\x00\x01\x02\x03\x04"),
            [66051]
        )

class TestPack(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(netstruct.pack(b""), b"")

    def test_not_enough(self):
        with self.assertRaises(netstruct.error):
            netstruct.pack(b"4i", 1, 2, 3)

    def test_too_many(self):
        with self.assertRaises(netstruct.error):
            netstruct.pack(b"4i", 1, 2, 3, 4, 5)

    def test_enough(self):
        self.assertEqual(
            netstruct.pack(b"4b", 1, 2, 3, 4),
            b"\x01\x02\x03\x04"
        )

    def test_string(self):
        self.assertEqual(
            netstruct.pack(b"b$i", b"Hello.", 42),
            b"\x06Hello.\x00\x00\x00\x2A"
        )


class TestIterUnpack(unittest.TestCase):
    def test_remaining(self):
        self.assertEqual(netstruct.iter_unpack(b"b$5i").next(), 21)

    def test_empty_send(self):
        it = netstruct.iter_unpack(b"b$5i")
        it.next()
        it.send(b"\x05")

        self.assertEqual(it.send(b""), 25)

    def test_remain_two(self):
        it = netstruct.iter_unpack(b"b$5i")
        it.next()

        self.assertEqual(it.send(b"\x05"), 25)

    def test_remain_three(self):
        it = netstruct.iter_unpack(b"b$5i")
        it.next()
        it.send(b"\x05")
        it.send(b"Hell")

        self.assertEqual(it.next(), 21)

    def test_total(self):
        it = netstruct.iter_unpack(b"b$4h")
        it.next()
        it.send(b"\x05Hello")

        self.assertEqual(
            it.send(b"\x01\x02\x03\x04\x05\x06\x07\x08"),
            [b"Hello", 258, 772, 1286, 1800]
        )

    def test_overage(self):
        it = netstruct.iter_unpack(b"b$4h")
        it.next()
        it.send(b"\x05Hello\x01\x02\x03\x04\x05\x06\x07\x08Test Here.")

        self.assertEqual(it.next(), b"Test Here.")

class TestObjUnpack(unittest.TestCase):
    def test_creation(self):
        obj = netstruct.obj_unpack(b"ih$5b")
        self.assertEqual(obj.remaining, 11)
        self.assertEqual(obj.result, None)
        self.assertEqual(obj.unused_data, b"")

    def test_remaining(self):
        obj = netstruct.obj_unpack(b"ih$5b")
        self.assertEqual(obj.feed(b"\x00\x02"), 9)

    def test_remain_two(self):
        obj = netstruct.obj_unpack(b"ih$5b")
        self.assertEqual(obj.feed(b"\x00\x02\x00\x04\x00\x00"), 5)

    def test_remain_three(self):
        obj = netstruct.obj_unpack(b"ih$5b")
        self.assertEqual(obj.feed(b"\x00\x00\x00\x00\x00\x02H"), 6)

    def test_remain_four(self):
        obj = netstruct.obj_unpack(b"ih$5b")
        self.assertEqual(
            obj.feed("\x00\x02\x00\x04\x00\x00\x05\x04\x03\x02\x01"),
            0
        )

    def test_result(self):
        obj = netstruct.obj_unpack(b"ih$5b")
        obj.feed("\x00\x02\x00\x04\x00\x00\x05\x04\x03\x02\x01")

        self.assertEqual(obj.remaining, 0)
        self.assertEqual(obj.unused_data, b"")
        self.assertEqual(obj.result, [131076, b"", 5, 4, 3, 2, 1])

        obj.feed(b"test string")
        self.assertEqual(obj.remaining, 0)
        self.assertEqual(obj.unused_data, b"test string")
        self.assertEqual(obj.result, [131076, b"", 5, 4, 3, 2, 1])


###############################################################################
# Execution
###############################################################################

if __name__ == '__main__':
    unittest.main()
