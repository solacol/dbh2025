#!/usr/bin/env python3
import struct
from itertools import cycle, product
from base64 import b64decode

# LIFO ^^
flag = [0x6139dcc5, 0x7e03abf2, 0x4e21d1dd, 0x5221f3ce, 0x4e3dceda, 0x7f25f4f4, 0x5239aada, 0x4646ceda, 0x5221e3cf, 0x6e39c1f3, 0x154ec8f1]
N = 10

AB = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
FREQUENCIES = { ord(a) : 1.0 / len(AB) for a in AB }

def xor(a, b):
    if isinstance(b, int):
        return bytes(x ^ b for x in a)
    assert len(a) >= len(b)
    return bytes(x ^ y for x, y in zip(a, cycle(b)))

def score(text):
    score = 0.0
    for c in text:
        if c in FREQUENCIES:
            score += FREQUENCIES[c]
    return score / len(text)

def breakXor(text):
    keys = sorted(range(256), key = lambda x: score(xor(text, x)))
    return keys[-N:]

def hamming(a, b):
    assert len(a) == len(b)
    return sum(bin(x).count("1") for x in xor(a, b))

def breakMultiXor(text, keySize):
    keys = [breakXor(text[i:len(text):keySize]) for i in range(keySize)]
    return [bytes(key) for key in product(*keys)]

flag = b''.join([struct.pack("<I", e) for e in flag])

keysize = 4
keys = breakMultiXor(flag, keysize)
for key in keys:
    text = xor(flag, key)
    try:
        decoded = b64decode(text, validate=True)
        decoded = decoded.decode('utf-8')
        print("0x{:8x}".format(struct.unpack("<I", key)[0]), ":", text.decode('utf-8'), ":", decoded)
    except:
        continue