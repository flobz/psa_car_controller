#!/bin/bash
cd /opt/data/cache/scratch/rcc_vnc
pkill -f "afl-fuzz.*harness_spi" 2>/dev/null
sleep 2
S=/opt/data/fuzz-nac/armel-sysroot
AFL=/opt/data/fuzz-nac/AFLplusplus/afl-fuzz
export QEMU_LD_PREFIX=$S AFL_SKIP_CPUFREQ=1 AFL_NO_UI=1 AFL_NO_AFFINITY=1 AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES=1 AFL_AUTORESUME=1
mkdir -p spi_out
$AFL -Q -i spi_in -o spi_out -M master   -x dict/spi.dict -p fast -m none -t 1000+ -- ./harness_spi @@ &
$AFL -Q -i spi_in -o spi_out -S sec1     -x dict/spi.dict -p fast -m none -t 1000+ -- ./harness_spi @@ &
$AFL -Q -i spi_in -o spi_out -S sec2     -x dict/spi.dict -p fast -m none -t 1000+ -- ./harness_spi @@ &
$AFL -Q -i spi_in -o spi_out -S sec3-cmplog -c 0 -x dict/spi.dict -p fast -m none -t 1000+ -- ./harness_spi @@ &
echo "launched; pgrep: $(pgrep -fc 'afl-fuzz.*harness_spi' 2>/dev/null || echo 0)"
