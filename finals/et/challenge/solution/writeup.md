# Write-Up Challenge ET
- Provided file `evidence.tar.gz` (md5sum: `ecff3aa9309c36a56375bd5752892f7c`)
- Untar/-zip
- Uncompress files

## Outer
- We have a picture of a device, the extracted firmware of this device, and a captured signal

### Analyze Device
- Raspberry Pico (`RP2040`)
- Transmitter `STX882` with antenna
- From this we already know (or just use a search engine of your choice) that we have to deal with `amplitude-shift keying` (`ASK`)

### Analyze Firmware
- `strings -a firmware.bin` shows some fancy stuff 
- Use `ghidra` etc. or simple `hexdump` to analyze
- Since we have to deal with `micropython`, the file `foobar.mpy` seems to be the one doing the logic
- This file is imported by `main.py`, which calls a function `foo`
- `foobar.mpy` is compiled `python` code (from original file `foobar.py`), but unlike `.cpy` it is not such easy to regain the original python source
- Extract the file by either mounting the `littlefs` filesystem or just use `dd` (offset `0x1b9000`) ... or even flashing back the firmware would work if some has a corresponding device
- Analyze the bytecode by using, e.g., [`mpy-tool`](https://github.com/micropython/micropython/blob/master/tools/mpy-tool.py)
- Starting with function `foo` we see the the pulse length is `400` and data is `double xor'ed` (function `e`, 1st key: `67`, 2nd key: `67-19`) before it is send (function `s`)
- Moreover we are able to identify the encoding procedure if we want to

### Analyze Signal
- From the filename (most receiver like `gnuradio` etc. save files like this, or just use any `sdr` software to find out and confirm):
  - Raw I/Q signal
  - `1.5M` samples per second
  - `433999998hz` center frequency
- For analyzing, there are several ways to do it: `universal radio hacker`, `sdrangel`, `inspectrum` or simple doing it manually
- We use [`inspectrum`](https://github.com/miek/inspectrum) ... it is also included in most distro repos
  - Set the `sample rate`
  - Use the shift-bars to get a clear view
  - Find the `symbol rate` by manually aligning symbols on spikes in the spectogram (it might be easier to do this for each signal block separately) ... zooming a bit in might help
  - Add an amplitude plot and align it
  - Adapt `Power max` and `Power min` to get a nice/clear square signal ... this almost not needed in default settings of `inspectrum`
  - Extract the symbols from the `amplitude graph` and decode
  - ... if done separately do it for each signal block ... the solution script is capable of decoding a single file if some is doing it step by step, which is recommended
- After decoding we have:
```
└──╼$ python sol_outer.py 
DEADBEEF
3d17b211702b0a34a986b24d1d4721c8
D34DB33F
f0VMRgEAAAAAAAAAAAABAAIAAwAgAAEAIAABAAQAAAC5mgEBAOsNADQAIAABAAAAAAAAADHSsgAx
20MxwLAEzYAxwOg2AQAAg/sKdCGD+zV8F4P7NX8Sg+swMcmxCvfhAdiD+GN/Auva6QkBAACD+AB0
9o0FAAAAAInHuZoBAQAx0rIAMdtDMcCwBM2Ag+x/ieYxyYP5f33Q6OAAAACIHoP7CnQEQUbr6ynO
MdtLg/kAdCEPthYx01ExybEIidqD4gH32oHiIIO47dHrMdPi7VlG4t/302jxyE4VaPPBOW5oz+Mh
UmjazkZGaNqqOVJo9PQlf2jazj1OaM7zIVJo3dEhTmjyqwN+aMXcOWGJ5rELMVyO/OL6gfPohn4N
weAIAdgxwIP4AHcZuZoBAQAx0rIfMdu7AgAAALAEzYC4f7peZInHMdtDahFqAmoCieExwLBmzYCJ
wjHAUFBXZmi6QGZqAonhahBRUGotVlKJ4THbswuwZs2AMdsxwEDNgFBRg+wEieEx0kIx2zHAsAPN
gA+2HCSDxARZWMNLaWxsc3dpdGNoIGFjdGl2YXRlZCBieSBzb2xhY29s
DEADBEEF
```

- It might be more or less obvious that `DEADBEEF` and `D34DB33F` are marker for start/end
- Using a simple check (like a [search engine](https://html.duckduckgo.com/html?q=hash%203d17b211702b0a34a986b24d1d4721c8)) it is easy to find out that `3d17b211702b0a34a986b24d1d4721c8` is a `md5 sum`
- The big block seems to be `base64` encoded
- Decoding and redirecting the output to a file shows it is an `ELF 32-bit invalid byte order (SYSV)` binary

## Inner
- We have an `ELF` file, so lets make it executable

### Analyze ELF
- Just executing the binary leads to a simple input (no output shown)
- `gdb`, `ghidra` or similar seems not to help here instantaneously
- Sidenote:
  - If some might use `strace` and is bruteforc'ing the input(s) it can be seen that something is transmitted over ethernet (destination: `127.186.94.100:47680`)
- There are several ways to solve it, incl `gdb`
- Since the `ELF` header is a minimal custom implementation, tools like `gdb` and `ghidra` etc. might need some feng shui to work with this
- We use a simple `objdump` approach to decompile the binary
- By using `readelf -h extracted_file.bin | grep -i 'size.*header'` we find the size of `ELF` and program header
- Since instructions will be located after those, we can simple extract them with `dd` by skipping the headers
- By extracting the entrypoint with, e.g., `readelf` we can use this information to disassemble the instructions with `objdump -b binary --adjust-vma=0x10020 -m i386 -M intel -D extracted_file.bin`
- The program basically does the following
  - Takes two inputs, whereby the first one has to be `5`
  - Decodes the following with `crc32` of the provided 2nd input
  - The most important part is
```
   100f6:	68 f1 c8 4e 15       	push   0x154ec8f1
   100fb:	68 f3 c1 39 6e       	push   0x6e39c1f3
   10100:	68 cf e3 21 52       	push   0x5221e3cf
   10105:	68 da ce 46 46       	push   0x4646ceda
   1010a:	68 da aa 39 52       	push   0x5239aada
   1010f:	68 f4 f4 25 7f       	push   0x7f25f4f4
   10114:	68 da ce 3d 4e       	push   0x4e3dceda
   10119:	68 ce f3 21 52       	push   0x5221f3ce
   1011e:	68 dd d1 21 4e       	push   0x4e21d1dd
   10123:	68 f2 ab 03 7e       	push   0x7e03abf2
   10128:	68 c5 dc 39 61       	push   0x6139dcc5
```

- We might have seen the string with the `killswitch`, it seems that the binary is checking if some value is `1` or `0`, and most likely it is set to `0`
- ... if it has not been set to `0`, it would have generated the destination IP by using the provided 2nd input, but since this is not the case, `127.186.94.100:47680` is used for all inputs
- ... decimal values of `186`, `94` and `100` result in `BA 5E 64`, and also the decimal value of the port `47680` results in `BA40`
- ... if this might be some kind of hint, we can either try `base64` or `base40`
- ... either way we just can bruteforce now

### Get the Flag
- Since `base64` seems to be more likely, we should try this first ... and do not forget to think of `LIFO`
- Get the flag:
```
└──╼$ python sol_inner.py 
0x28739997 : REJIe2pVJHRfYjRzMWNfcmVWM3JzMW5nXzRzdXJFfQ== : DBH{jU$t_b4s1c_reV3rs1ng_4surE}
0x27779997 : RENFe2tYJHViYjVuMWJicmRXM3NuMW1aXzVudXNIfQ92 : DCE{kX$ubb5n1bbrdW3sn1mZ_5nusH}v
0x28779997 : RENIe2tVJHVfYjVzMWJfcmRWM3NzMW1nXzVzdXNFfQ9= : DCH{kU$u_b5s1b_rdV3ss1mg_5susE}
```

## Flag
`DBH{jU$t_b4s1c_reV3rs1ng_4surE}`