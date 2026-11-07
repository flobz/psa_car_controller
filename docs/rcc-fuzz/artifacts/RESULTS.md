# RCC head-unit remote attack-surface fuzzing — results

Date: 2026-11-07 ~21:11 UTC. Target: Bosch RCC (rfs.A2.new), phone->HU surfaces over usb+ (tcp 36735-36834, udp>=1024, mdns udp/5353).
Method: QEMU user-mode ARM harnesses (AFL++ -Q), targets loaded at fixed bases; guard-page detection.

## out: execs=67,847,846 edges=255 crashes=0 hangs=54
## spi_out: execs=22,096,718 edges=295 crashes=0 hangs=3
## disc_out: execs=1,702,555 edges=260 crashes=0 hangs=4
## mdns_out: execs=4,177,449 edges=145 crashes=0 hangs=0

## TOTAL: execs=95,824,568 crashes=0 hangs=61

## Targets
- out: libvncviewersdk.so.0.0.0 — CMsgReader::readRect @0x68b04 / readRectHeader @0x6b2e0 + Hextile/ZRLE/RRE/TRLE/Zlib/Raw/JPEG decoders (CVE-2008-4770 lead). VERDICT: fixed in this 2010 build (GCC 4.4.4); bounds checks present; 0 crashes.
- spi_out: libmirrorlinkspi_so.so — bDeserializeNaviPayload @0x899d0, bDeserializePayload @0x920c0, onDeserialized*Data sinks. Engine libvnccdbsdk.so.0.0.0 audited: length-guarded reads, payload cap 8100B. 0 crashes (earlier crashes were harness artifacts: stubbed operator new/_M_create).
- disc_out: spi_tclMLVncDiscoverer::vProcessAppList @0xaf760 (app-list XML from phone). 0 crashes.
- mdns_out: /usr/bin/mdnsd (mDNSResponder Jan 2021) DNS packet parser @0x27cfc (udp/5353). 0 crashes.

## Crash triage
All crashes/hangs observed were harness artifacts (NULL from stubbed C++ allocators, stub vtable callbacks, EOF spin) — no reproducible crash inside target binary code. No exploitable RCE found on the tested surfaces.

## Layout
- artifacts/<camp>/<inst>.stats, .queue/, .crashes/, .hangs/ — AFL++ outputs
- artifacts/harness_*.cpp, relaunch_*.sh, dict/, seeds/ — reproducible kit
- instabox_results/ — corpora pulled from instabox fuzz1 (bout/sout/dout)

## Reproduce
```
cd /opt/data/cache/scratch/rcc_vnc
bash relaunch_vnc.sh   # or relaunch_spi.sh / relaunch_disc.sh / relaunch_mdns.sh
```