#!/bin/bash
cd /opt/data/cache/scratch/rcc_vnc
pkill -f "afl-fuzz.*harness_mdns" 2>/dev/null
sleep 2
S=/opt/data/fuzz-nac/armel-sysroot
AFL=/opt/data/fuzz-nac/AFLplusplus/afl-fuzz
export QEMU_LD_PREFIX=$S AFL_SKIP_CPUFREQ=1 AFL_NO_UI=1 AFL_NO_AFFINITY=1 AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES=1 AFL_AUTORESUME=1
mkdir -p mdns_out
cat > dict/mdns.dict <<'DICT'
kw_ptr="\xc0\x0c"
kw_lbl="\x03www"
kw_srv="\x04_srv"
kw_txt="\x04_txt"
DICT
$AFL -Q -i mdns_in -o mdns_out -M master   -x dict/mdns.dict -p fast -m none -t 2000+ -- ./harness_mdns @@ &
$AFL -Q -i mdns_in -o mdns_out -S sec1     -x dict/mdns.dict -p fast -m none -t 2000+ -- ./harness_mdns @@ &
$AFL -Q -i mdns_in -o mdns_out -S sec2     -x dict/mdns.dict -p fast -m none -t 2000+ -- ./harness_mdns @@ &
$AFL -Q -i mdns_in -o mdns_out -S sec3-cmplog -c 0 -x dict/mdns.dict -p fast -m none -t 2000+ -- ./harness_mdns @@ &
echo "launched; pgrep: $(pgrep -fc 'afl-fuzz.*harness_mdns' 2>/dev/null || echo 0)"
