#!/bin/sh

# Hugh O'Brien obrien.hugh@gmail.com 2014-05-25
# Program the nRF51822, based on nRF51_Series_Reference_Manual_v2.1.pdf
# Uses SEGGER JLINK

[ -z $(command -v JLinkExe) ] && echo "Put Segger's JLinkExe on the path" && exit

application="a.hex"

[ ! -f "$application" ] && echo "$application not found" && exit

device="NRF52"

speed="1000" #unit is KHz, nordic docs recommed 1MHz

wait_time="300" #unit is ms

write_32bit="w4"

base_addr="4001e" #non-volatile memory controller

config_offset="504" #config register, 0 RO, 1 RW, 2 ERASEable

enable_write="1"

set_device="Device"
set_speed="speed"
write_program="loadbin"
reset_device="rx" #use the 'delay after reset' version
start_device="g"
close_and_quit="qc"

script_file="flash.jlink"

rm $script_file 2>/dev/null #suppress error if not found

touch $script_file

################################################
# put commands into script
################################################

echo $set_device $device >> $script_file
echo $set_speed $speed >> $script_file
echo $write_32bit $base_addr$config_offset $enable_write >> $script_file
echo $write_program $soft_device $region0_start >> $script_file
echo $write_program $application $region1_start >> $script_file
echo $reset_device $wait_time >> $script_file

echo $start_device >> $script_file

echo $close_and_quit >> $script_file





JLinkExe $script_file



rm $script_file
