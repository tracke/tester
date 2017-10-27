# try and start wireless here since it didn't work in bootlocal.sh
sleep 1
sudo /usr/local/sbin/wpa_supplicant -i wlan0 -c /opt/wpa_supplicant.conf &
sleep 1
sudo /sbin/udhcpc -i wlan0 &

sudo iwconfig>/opt/status
 
