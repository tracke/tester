#!/bin/sh



# Hugh O'Brien obrien.hugh@gmail.com 2014-05-25

# Erase the nRF51822, based on nRF51_Series_Reference_Manual_v2.1.pdf

# Uses SEGGER JLINK



#[ -z $(command -v JLinkExe) ] && echo "Put Segger's JLinkExe on the path" && exit

device="nrf52"
speed="1000" #unit is KHz, nordic docs recommed 1MHz
wait_time="300" #unit is ms



write_32bit="w4"
base_addr="4001e" #non-volatile memory controller
config_offset="504" #config register, 0 RO, 1 RW, 2 ERASEable
eraseall_offset="50c" # 0 NOP, 1 ERASE, includes user registers (UICRs)

#specific pages in regions 0 or 1 may also be erased

eraseable="2"
do_erase="1"


set_device="Device"
set_speed="speed"
wait="sleep"
reset_device="r"
close_and_quit="qc"

script_file="erase.jlink"

rm $script_file 2>/dev/null #suppress error if not found

touch $script_file


echo $set_device $device >> $script_file
echo $set_speed $speed >> $script_file

echo $write_32bit $base_addr$config_offset $eraseable >> $script_file
echo $write_32bit $base_addr$eraseall_offset $do_erase >> $script_file
echo $wait $wait_time >> $script_file
echo $reset_device >> $script_file
echo $close_and_quit >> $script_file

./JLinkExe $script_file
#rm $script_file
