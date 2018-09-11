clear
if [ -f "/home/pi/update_script.sh" ]
then
  chown pi:root /home/pi/update_script.sh
  chmod 754 /home/pi/update_script.sh
fi
if [ -f "/home/ink/UpdateFiles/Sensors/lastUpdate" ]
then
  printf 'Starting Program Update\n\n'
  chmod 664 /home/ink/UpdateFiles/Sensors/lastUpdate
else
  printf 'Starting Program Install\n\n'
fi
mkdir /mnt/supernas 2>/dev/null
mkdir /home/ink 2>/dev/null
mkdir /home/ink/UpdateFiles 2>/dev/null
mkdir /home/ink/UpdateFiles/Sensors 2>/dev/null
mkdir /home/ink/UpdateFiles/Sensors/auto_start 2>/dev/null
mkdir /home/ink/UpdateFiles/Sensors/sensor_modules 2>/dev/null
mkdir /home/ink/UpdateFiles/Sensors/upgrade 2>/dev/null
mount -t cifs //192.168.7.15/Public /mnt/supernas -o username=myself,password='123'
sleep 1
printf 'Connected to SuperNAS OK\nCopying files...' # Copy new files off my "SuperNAS" to the local device
cp -R /mnt/supernas/RaspberryPi/Sensors/E-InkServer /home/ink
cp -R /mnt/supernas/RaspberryPi/Sensors/ClientSensors /home/ink/UpdateFiles/Sensors
cp /home/ink/install_update_script.sh /home/pi/update_script2.sh
# make sure proper permissions are on the new folders and files
chown pi:root /home/ink -R
chown pi:root /home/pi -R
chmod 755 /home/ink -R
chmod 644 /home/ink/UpdateFiles/Sensors/* 2>/dev/null
chmod 644 /home/ink/UpdateFiles/Sensors/auto_start/* 2>/dev/null
chmod 644 /home/ink/UpdateFiles/Sensors/sensor_modules/* 2>/dev/null
chmod 644 /home/ink/UpdateFiles/Sensors/upgrade/* 2>/dev/null
chmod 644 /home/pi/Downloads/* 2>/dev/null
umount /mnt/supernas
printf '\nPermissions Set & Disconnected from SuperNAS OK\n\nUpdating AutoStart, AutoWifi, & fake-hwclock\n'
echo '*/1 * * * * fake-hwclock' > /home/pi/tmp34.txt
echo '*/1 * * * * bash /home/ink/autoStart_eink.sh' >> /home/pi/tmp34.txt
echo '*/1 * * * * bash /home/ink/autoStartHTTP.sh' >> /home/pi/tmp34.txt
crontab -u root /home/pi/tmp34.txt
rm -f /home/pi/tmp34.txt
if [ ! -f "/home/ink/UpdateFiles/Sensors/lastUpdate" ]
then
  printf 'Installing interfaces\n\nSSID: SensorWifi\nWPA-PSK: 2505512335\nIP: 192.168.10.5\n\n'
  cat >> /etc/network/interfaces << "EOF"

allow-hotplug wlan0
iface wlan0 inet static
  address 192.168.10.5
  netmask 255.255.255.0
  gateway 192.168.10.1
  dns-nameservers 192.168.10.1
  wpa-ssid SensorWifi
  wpa-psk 2505512335
EOF
  chmod 644 /etc/network/interfaces
  printf '\nStarting System Update\n\n\n'
  apt-get -y remove wolfram-engine
  apt-get update
  apt-get -y upgrade
  printf '\n\n\nInstalling Dependencies\n\n\n'
  sudo apt-get -y install python3-pip libatlas-base-dev fonts-freefont-ttf zlib1g-dev libfreetype6-dev liblcms1-dev lighttpd libjpeg8-dev fake-hwclock
  sudo pip3 install RPi.GPIO spidev qrcode Pillow requests
  printf '\nInstall Done\n'
else
  printf '\nUpdate Done\n'
fi
date > /home/ink/UpdateFiles/Sensors/lastUpdate
mv /home/pi/update_script2.sh /home/pi/update_script.sh