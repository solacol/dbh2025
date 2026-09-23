# Write-Up Challenge Pump
- The provided snippet looks like some kind of memory dump:
```
fffff805`1f484d88  00000000`000316f0 00000000`00140001
fffff805`1f484d98  00000000`00000003 00000000`00000000
fffff805`1f484da8  72654720`6d6f7246 74697720`796e616d
fffff805`1f484db8  00000000`333c2068 764e5759`73393263
fffff805`1f484dc8  7a6c5859`7a424362 77734853`43524549
fffff805`1f484dd8  6a6c6b54`664e6a62 7a593362`7339565a
fffff805`1f484de8  7456465a`666c4854 39646d54`78774763
fffff805`1f484df8  00000000`00000000 00000000`00000000
fffff805`1f484e08  00000000`00000000 00000000`00000000
fffff805`1f484e18  00000000`00000000 00000000`00000000
fffff805`1f484e28  00000000`00000000 00000000`00000000
fffff805`1f484e38  ffffc28e`874a4080 ffff4267`6694881a
fffff805`1f484e48  00000000`00400a02 ffffffff`ffffffff
```

## Analyze
- Addresses in the first column are clearly kernelmode ones -> we can ignore them for sure
- Some might guess, that `QWORDS` like `00000000 00000000` can be ignored too
- ... checking for printable chars is also a way to do it
- We should deal with the remaining part:
```
fffff805`1f484da8  72654720`6d6f7246 74697720`796e616d
fffff805`1f484db8  00000000`333c2068 764e5759`73393263
fffff805`1f484dc8  7a6c5859`7a424362 77734853`43524549
fffff805`1f484dd8  6a6c6b54`664e6a62 7a593362`7339565a
fffff805`1f484de8  7456465a`666c4854 39646d54`78774763
```

- It is a memory dump so we might have to take care of little endian
- ... and do not forget we have to deal with `QWORDS`, hence either split them up to `DWORDS` or handle them accordingly:
```bash
└──╼$ cat pump
fffff805`1f484d88  00000000`000316f0 00000000`00140001
fffff805`1f484d98  00000000`00000003 00000000`00000000
fffff805`1f484da8  72654720`6d6f7246 74697720`796e616d
fffff805`1f484db8  00000000`333c2068 764e5759`73393263
fffff805`1f484dc8  7a6c5859`7a424362 77734853`43524549
fffff805`1f484dd8  6a6c6b54`664e6a62 7a593362`7339565a
fffff805`1f484de8  7456465a`666c4854 39646d54`78774763
fffff805`1f484df8  00000000`00000000 00000000`00000000
fffff805`1f484e08  00000000`00000000 00000000`00000000
fffff805`1f484e18  00000000`00000000 00000000`00000000
fffff805`1f484e28  00000000`00000000 00000000`00000000
fffff805`1f484e38  ffffc28e`874a4080 ffff4267`6694881a
fffff805`1f484e48  00000000`00400a02 ffffffff`ffffffff

└──╼$ dwords=$(sed -e '1,2d' pump | sed -e '6,$d' | sed -e 's/`/ /g' | awk -F' ' '{print $4" "$3" "$6" "$5}' | tr '\n' ' ') && for dword in $dwords; do echo $dword | tac -rs ..; done | xxd -r -p
From Germany with <3c29sYWNvbCBzYXlzIERCSHswbjNfTkljZV9sb3YzTHlfZFVtcGwxTmd9
```

## Get the Flag
- The result seems to be a mix out of plaintext (`From Germany with <3`) and `base64` encoded text (`c29sYWNvbCBzYXlzIERCSHswbjNfTkljZV9sb3YzTHlfZFVtcGwxTmd9`)
- ... so all in one line:
```bash
└──╼$ dwords=$(sed -e '1,2d' chall | sed -e '6,$d' | sed -e 's/`/ /g' | awk -F' ' '{print $4" "$3" "$6" "$5}' | tr '\n' ' ') && for dword in $dwords; do echo $dword | tac -rs ..; done | xxd -r -p | sed 's/.*<3//' | tr -d '\0' | base64 -d
solacol says DBH{0n3_NIce_lov3Ly_dUmpl1Ng}
```

## Flag
`DBH{0n3_NIce_lov3Ly_dUmpl1Ng}`