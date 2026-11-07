#!/bin/bash
# Relaunch RCC VNC viewer fuzz workers (idempotent: kills existing first)
cd /opt/data/cache/scratch/rcc_vnc
pkill -f "afl-fuzz.*harness_vnc" 2>/dev/null
sleep 2
S=/opt/data/fuzz-nac/armel-sysroot
AFL=/opt/data/fuzz-nac/AFLplusplus/afl-fuzz
export QEMU_LD_PREFIX=$S AFL_SKIP_CPUFREQ=1 AFL_NO_UI=1 AFL_NO_AFFINITY=1 AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES=1 AFL_AUTORESUME=1
mkdir -p out
$AFL -Q -i in -o out -M master   -x dict/rfb.dict -p fast -m none -t 1000+ -- ./harness_vnc @@ &
$AFL -Q -i in -o out -S sec1     -x dict/rfb.dict -p fast -m none -t 1000+ -- ./harness_vnc @@ &
$AFL -Q -i in -o out -S sec2     -x dict/rfb.dict -p fast -m none -t 1000+ -- ./harness_vnc @@ &
$AFL -Q -i in -o out -S sec3-cmplog -c 0 -x dict/rfb.dict -p fast -m none -t 1000+ -- ./harness_vnc @@ &
echo "launched; pgrep: $(pgrep -fc 'afl-fuzz.*fuzz-vnc' 2>/dev/null || echo 0)"
