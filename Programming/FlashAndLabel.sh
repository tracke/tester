#!/bin/bash

# flash board and print label 
# ==================================================
# Revision    Date              Change
#     1       2/07/20176      Initial Creation to perform  FLASH and LABEL functions on 
#     -         --                    a Raspberry Pi 2
# ==================================================
ARGNO=3
BAT_REV=2.0
FWARE_PATH="/FWARE/"
# ==================================================

#check for correct no of arguments and assign them
if [ $# -lt $ARGNO ]
 then
 echo "!!! USAGE - PROGRAMandLABEL <PART NUMBER> <PRODUCT><FWARE>  !!!"
   exit 1
fi
PN=$1
PRODUCT=$2
FWARE=$3 

VAR=0
WO=123

TITLE="FLASH PROGRAM AND LABEL $PN $PRODUCT"

#cfg file has name of firmware image to use
FWARE_CFG=$FWARE_PATH$PN"/"$PN".cfg"  
if [ -f $FWARE_CFG ]
  then
    echo "Found $FWARE_CFG"
else
    echo "Could not find $FWARE_CFG"
    exit 1
fi
FWARE_HEX=$(<$FWARE_CFG)
FWARE=$FWARE_PATH$PN"/"$FWARE_HEX
REV_HEX="${FWARE_HEX#*r}"
FWARE_REV="${REV_HEX%.*}"
echo FWARE REV:$FWARE_REV

if [ -f $FWARE ]; then
   echo "$FWARE found"
else
   echo "$FWARE NOT FOUND"
   exit
fi

echo -n "ENTER WORK ORDER NUMBER: "
read WO
echo ${#WO}
#if (${#WO}==3) ||  echo "ERROR"

PRINTER="DYMO"
LABEL_POS=1
clear
echo "******************************************************"
echo "** $PRODUCT Programmer and Label Printer "
echo "** Rev $BAT_REV"
echo "******************************************************"
echo "** PRODUCT:$PRODUCT"
echo "** PART:$PN "
echo "** PO: $WO"
echo "** FIRMWARE: $FWARE_HEX"
echo "** PRINTER: $PRINTER"
echo "** LABEL: $LABEL_POS"
echo "******************************************************"
echo  "PLACE BOARD ON PROGRAMMING FIXTURE AND PRESS ANY KEY TO CONTINUE"
read x
cd /home/pi/JLink_Linux_V612j_arm

echo -n "ERASE: "
JLinkExe erase.jlink >/dev/null && echo "PASSED"|| echo "FAILED"

echo -n "PROGRAM: "


echo "VERIFY"

cd /home/pi/JLink_Linux_V612h_arm
get_HWID=`./JLinkExe get_hwid.jlink | grep 100000A4 || echo"JLINK FAILED"`
HWID_SP="${get_HWID#*=}"
HWID="$(echo $HWID_SP | tr -d ' ')"
echo "HWID:$HWID"
echo "$HWID_SP"
cd ~

BARCODE=$PN"."$VAR"-"$WO"-"$HWID
echo $BARCODE
exit


exit
