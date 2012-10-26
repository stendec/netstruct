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


###############################################################################
# Execution
###############################################################################

if __name__ == '__main__':
    unittest.main()
