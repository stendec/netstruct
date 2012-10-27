NetStruct
=========

NetStruct is a [struct](http://docs.python.org/library/struct.html)-like
module for Python designed to make it a bit easier to send and received packed
binary data.

NetStruct is available under the [Apache License, Version 2.0]
(http://www.apache.org/licenses/LICENSE-2.0.html).


Install
=======

NetStruct can be installed using [pip](http://http://pypi.python.org/pypi/pip):

    pip install netstruct

You can also grab the latest code from the [git](http://git-scm.com/)
repository:

    git clone git://github.com/stendec/netstruct

NetStruct runs on [Python 2.6+](http://python.org). Python 3 should work as
well, but is currently untested.


Differences from ``struct``
===========================

NetStruct has two differences from ``struct``.

First, it defaults to using network byte-order, rather than native byte-order,
on the assumption that you'll be using it to send data over the network and,
thus, it's saving you time.

Additionally, the generated strings don't have any padding when using
non-native byte-order.

Second, NetStruct supports a new formatting character, the dollar sign (``$``).
The dollar sign represents a variable-length string, encoded with its length
preceeding the string itself. To accomplish this, the formatting character
directly before the dollar sign is assumed to represent the string's length.


Examples
========

This is as basic as it gets.

```python
>>> import netstruct
>>> netstruct.pack("b$", "Hello World!")
'\x0cHello World!'
```

Alternatively.

```python
>>> netstruct.unpack("b$", "\x0cHello World!")
['Hello World!']
```

You can get a bit more complex, if you'd like.

```python
>>> netstruct.pack("ih$5b", 1298, "largeBiomes", 0, 0, 1, 0, 8)
'\x00\x00\x05\x12\x00\x0blargeBiomes\x00\x00\x01\x00\x08'
```

And, of course, you can unpack complex data too.

```python
>>> netstruct.unpack("bh$h$i", "'\x00\x07stendec\x00\tlocalhost\x00\x00c\xdd")
[39, 'stendec', 'localhost', 25565]
```

You just have to be sure to use a long enough string.

```python
>>> netstruct.unpack("bh$h$i", "'\x00\x07stendec\x00\tlocalhost\x00")
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "site-packages/netstruct.py", line 275, in unpack
    return NetStruct(format).unpack(data)
  File "site-packages/netstruct.py", line 165, in unpack
    raise error("unpack requires a string argument of length %d" % (len(data) + out))
struct.error: unpack requires a string argument of length 25
```

But wait, you say. How am I supposed to provide a long enough string to
unpack the data when I can't possibly know the length ahead of time?
Simply put, you *can* know the length.

```python
>>> it = netstruct.iter_unpack("ih$5b")
>>> it.next()
11
```

The ``iter_unpack`` function returns an iterator. Each time you call that
iterator's .next() or .send() methods, it can return one of two values. Either
it'll return the number of bytes it wants you to read next, or it'll return
the completed object.

Let's continue from above, shall we?

```python
>>> it.send("\x00\x00\x05\x12\x00\x0b")
16
>>> it.send("largeBiomes")
5
>>> it.send("\x00\x00\x01\x00\x08   more")
[1298, 'largeBiomes', 0, 0, 1, 0, 8]
```

There. I've sent enough data, so it returned the completed list of the
unpacked data. At this point, I can take my data, and do whatever it is I want
with it.

But wait! I just sent too much data to that iterator, and now I've lost some
of my string, haven't I? That's not a problem either. You can call the iterator
one final time and it will return the unconsumed remainder of the data.

```python
>>> it.next()
'   more'
```

It's just that simple. Of course, not everyone likes iterators, even if they
*are* quicker and less memory intensive than a class instance. NetStruct is
prepared, with its ``Unpacker`` class and ``obj_unpack``. Let's try that last
example one more time.

```python
>>> obj = netstruct.obj_unpack("ih$5b")
>>> obj.remaining
11
>>> obj.feed("\x00\x00\x05\x12\x00\x0b")
16
>>> obj.feed("largeBiomes")
5
>>> obj.feed("\x00\x00\x01\x00\x08   more")
0
>>> obj.result
[1298, 'largeBiomes', 0, 0, 1, 0, 8]
>>> obj.unused_data
'   more'
```

Enjoy.