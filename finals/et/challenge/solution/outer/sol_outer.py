#!/usr/bin/env python3
ALLFILES = True
DEBUG = False
XOR = True
THRESHOLD = 4.0
KEY = 67

def xor(data, key):
    enc = ""
    for c in data.decode('utf-8'):
        enc += chr(ord(c) ^ key)
    return enc.encode('utf-8')

def decode(FILE, res):
    symbols = open(FILE).read()
    symbols = [s.strip() for s in symbols.split(',')]
    symbols = [s for s in symbols if s]
    symbols = [1 if float(f) > THRESHOLD else 0 for f in symbols]

    binary = []
    low_cnt = 0
    high_cnt = 0
    last_val = None
    for i in symbols:
        if i == 0:
            low_cnt += 1
            last_val = 0
        else:  # i == 1
            if last_val == 0:
                # decode bit
                if high_cnt == 7:
                    pass  # ignore sync
                elif high_cnt == 1 and low_cnt == 3:
                    binary.append(0)
                elif high_cnt == 3 and low_cnt == 1:
                    binary.append(1)
                else:
                    if DEBUG:
                        print(f"Error decoding bit: high_cnt={high_cnt} low_cnt={low_cnt}")
                low_cnt = 0
                high_cnt = 0
            high_cnt += 1
            last_val = 1

    while len(binary) % 8:
        binary.append(0)

    text = []
    for i in range(0, len(binary), 8):
        b = 0
        for j in range(8):
            b <<= 1
            b |= binary[i+j]
        text.append(b)

    try:
        if XOR:
            data = bytes(text).decode('utf-8')
            if ALLFILES:
                res += xor(xor(data.encode('utf-8'), KEY - 19), KEY).decode('utf-8')
                return res
            else:
                print(xor(xor(data.encode('utf-8'), KEY - 19), KEY), end='', flush=True)
        else:
            print(bytes(text).decode('utf8'), end='', flush=True)
    except UnicodeDecodeError as err:
        if DEBUG:
            print(f"Error decoding: {err}")

def main():
    AMPLITUDES_FILE = 'syms.txt'
    RESULT = ""
    if ALLFILES:
        for i in range(13):
            AMPLITUDES_FILE = 'syms' + hex(i) + '.txt'
            if DEBUG:
                print(AMPLITUDES_FILE)
            RESULT = decode(AMPLITUDES_FILE, RESULT)
        print(RESULT, end='', flush=True)
    else:
        decode(AMPLITUDES_FILE, RESULT)

if __name__ == "__main__":
    main()
