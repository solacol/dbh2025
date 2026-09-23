# Write-Up Challenge Ydna
- Provided file `dbh.pcap` (md5sum: `125fe3da3a467d68bad71457c430aea8`)

## Analyze Part 1
- Use `wireshark` or similar
- Findings:
  * Lots of `NTP packets
  * `Follow UDP Stream` -> `solacol: "As soon you arrive, all your time belongs to andy." --- andy: "For a wise anteater, size is everything."`

## Analyze Part 2
- From the text we might get some small hints: 
  * `arrive`
  * `time` -> also indicated since we have to deal with `NTP`
  * `anteater`
  * `size`
  * even `andy` might be one
- Only a few might be needed to find a solution:
  * `arrive`
  * `time`
  * `size`
- A quick online-search might lead to `https://tranalyzer.com`, nicknamed `anteater` (mascot is called `andy`)
- Searching in the tutorials section, e.g., `arrive`, might lead to a [tutorial about packet inter arrival time](https://tranalyzer.com/tutorial/trafficmining#the-packet-length-inter-arrival-time-distribution)

## Get the Flag Part 1
- You do not need to use the `T2 aka Tranalyzer`, it is solvable via simple `python foo` or even `Excel`
- For this writeup we use `T2`
  * [Basic setup T2](https://tranalyzer.com/tutorial/installation)
  * Additional setup
    * `t2build pktSIATHisto`
    * `printf '%s\n' basicFlow pktSIATHisto txtSink > ~/.tranalyzer/plugins/plugins.txt` 

## Get the Flag Part 2
- Use `T2` to create flows from `dbh.pcap`:
  * `t2 -r dbh.pcap`
  * `statGplt --ps-iat dbh_flows.txt`
- Use `T2` to plot the results, e.g., by using `gnuplot`:
  * `t2plot -r 0 -ws 1920,1080 dbh_flows_ps_iat.txt`
- Get the flag:
  * Some rotation and scaling might be needed to get a `2D` picture
  * `DBH{andY_th3_antE4t3r_yamyam}`

## Flag
`DBH{andY_th3_antE4t3r_yamyam}`