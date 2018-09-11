'''
    KootNet Sensors is a collection of programs and scripts to deploy,
    interact with, and collect readings from various Sensors.  
    Copyright (C) 2018  Chad Ermacora  chad.ermacora@gmail.com  

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

import os, socket, pickle, epd2in7b
import RPi.GPIO as GPIO
from time import sleep, strftime
from gpiozero import CPUTemperature
from urllib.request import urlopen
from PIL import ImageFont

socket.setdefaulttimeout(2)
save_to = "/home/pi/Downloads/"

ip_list = "192.168.10.11","192.168.10.12", "192.168.10.13","192.168.10.14", \
          "192.168.10.15", "192.168.10.16", "192.168.10.17", "192.168.10.18"#, \
#          "192.168.10.19", "192.168.10.20", "192.168.10.21", "192.168.10.22"

font1 = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 15)
font2 = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 13)

epd = epd2in7b.EPD()
epd.init()

key1 = 5
key2 = 6
key3 = 13
key4 = 19

timer_hit = 0
key_hit1 = 0
key_hit2 = 0
key_hit3 = 0
key_hit4 = 0

GPIO.setup(key1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(key2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(key3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(key4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def get_system_info():
    cpu = CPUTemperature()
    frame_black = [0] * int((epd.width * epd.height / 8))
    frame_red = [0] * int((epd.width * epd.height / 8))
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        testIP = (s.getsockname()[0])
        s.close()
        
    except BaseException:
        testIP = "0.0.0.0"
        
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        uptime_string = round(uptime_seconds / 60,0)
    
    localfile = open('/home/pi/config/LastUpdated.txt','r')
    lastUpgrade = localfile.read()
    localfile.close()

    epd.draw_string_at(frame_black,1,1, str(socket.gethostname()), font1, 1)
    epd.draw_string_at(frame_red,1,20, str(testIP), font1, 1)
    epd.draw_string_at(frame_black,1,40, "CPU Temp:" + str(round(cpu.temperature, 1)) + "c", font1, 1)
    epd.draw_string_at(frame_black,1,60, "UpTime:" + str(int(uptime_string)) + " Min", font1, 1)
    epd.draw_string_at(frame_black,1,100, "UpGrade Files:", font1, 1)
    epd.draw_string_at(frame_black,1,120, str(lastUpgrade[4:10]) + " " + str(lastUpgrade[11:16]), font1, 1)
    epd.draw_string_at(frame_black,1,180, "Screen Updated", font1, 1)
    epd.draw_string_at(frame_black,1,240, str(strftime("%b-%d %H:%M")), font1, 1)
    epd.display_frame(frame_black, frame_red)
    
def get_sensor_info():
    screenMessage_online = "Online\n"
    screenMessage_offline = "Offline\n"
    offline_count = 1
    frame_black = [0] * int((epd.width * epd.height / 8))
    frame_red = [0] * int((epd.width * epd.height / 8))

    for ip in ip_list:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print1 = True
        try:
            sock.connect((ip,10065))
            sock.send(b'datagt')
            tmp = str(pickle.loads(sock.recv(512)))
            data = tmp.split(",")
            print("Connected to " + str(ip) + " & Data Recived")
            sock.close()
        except:
            print1 = False

        if print1 == True:
            # Display the data on the screen
            screenMessage_online = screenMessage_online + str(data[1][6:13])
            screenMessage_online = screenMessage_online + " Up " + str(data[2]) + " Min\n"

        else:
            print(ip + " Failed")
            screenMessage_offline = screenMessage_offline + str(ip)[-3:] + ","
            if offline_count == 4:
                screenMessage_offline = screenMessage_offline + "\n"
                offline_count = 0
            offline_count = offline_count + 1

    epd.draw_string_at(frame_black,1,1, screenMessage_online, font2,1)
    epd.draw_string_at(frame_red,1,170, screenMessage_offline, font1,1)
    epd.draw_string_at(frame_black,1,240, str(strftime("LU:%a:%d %H:%M")), font2,1)
    epd.display_frame(frame_black, frame_red)

def download_sensor_files():
    screen_data1 = "DL Pri SQLiteDB\n"
    frame_black = [0] * int((epd.width * epd.height / 8))
    frame_red = [0] * int((epd.width * epd.height / 8))

    for ip in ip_list:
        try:
            remote_database = urlopen("http://" + str(ip) + ':8009/SensorPrimaryDatabase.sqlite')
            localfile = open(save_to + "SensorPrimaryDatabase" + str(ip[-3:]) + ".sqlite",'wb')
            localfile.write(remote_database.read())
            remote_database.close()
            localfile.close()
            screen_data1 = screen_data1 + str(ip) + " DL: OK\n"
            print(ip + " Connection OK")
        except:
            screen_data1 = screen_data1 + str(ip) + " Failed\n"
            print(ip + " Connection Failed")
            
    epd.draw_string_at(frame_black,1,1,screen_data1,font2,1)
    epd.display_frame(frame_black, frame_red)

def reboot_sensors():
    rebootMessage = "Reboot Sensors\n"
    frame_black = [0] * int((epd.width * epd.height / 8))
    frame_red = [0] * int((epd.width * epd.height / 8))
    
    for ip in ip_list:
        sockG1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sockG1.connect((ip, 10065))
            sockG1.send(b'reboot')
            sockG1.close()
            rebootMessage = rebootMessage + str(ip) + " OK\n"
        except:
            rebootMessage = rebootMessage + str(ip) + " Fail\n"
    
    print(rebootMessage)
    epd.draw_string_at(frame_red,1,1,rebootMessage,font1,1)
    epd.display_frame(frame_black, frame_red)

def upgrade_sensor_progs():
    upgrade_message = "Sensors UpGraded\n"
    frame_black = [0] * int((epd.width * epd.height / 8))
    frame_red = [0] * int((epd.width * epd.height / 8))
    
    for ip in ip_list:
        sockG = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sockG.connect((ip, 10065))
            sockG.send(b'inkupg')
            upgrade_message = upgrade_message + str(ip) + " OK\n"
            sockG.close()
        except:
            upgrade_message = upgrade_message + str(ip) + " Failed\n"

    print(upgrade_message)
    epd.draw_string_at(frame_black,1,1,upgrade_message,font2,1)
    epd.display_frame(frame_black, frame_red)

while True:
    timer_hit = timer_hit + 1
    message_text = ""

    key1state = GPIO.input(key1)
    key2state = GPIO.input(key2)
    key3state = GPIO.input(key3)
    key4state = GPIO.input(key4)

    if timer_hit > 25:  # After 10 seconds, reset timer_hit and all the key_hit
#        print("timer_hit > 10\nkey_hit's reset")
        timer_hit = 0
        key_hit1 = 0
        key_hit2 = 0
        key_hit3 = 0
        key_hit4 = 0

    if key1state == False:  
        if key_hit1 == 0:  # Show sys info and reset counters.  
            print("Key1 Op: Showing SysInfo")
            key_hit2 = 0
            key_hit3 = 0
            key_hit4 = 0
            get_system_info()
            key_hit1 = key_hit1 + 1

        elif key_hit1 == 1:
            frame_black = [0] * int((epd.width * epd.height / 8))
            frame_red = [0] * int((epd.width * epd.height / 8))

            print("Key1 Op: Updating Files")
            message_text = "Updating Device\nApplications\n autoInk\n" + \
            " Update " + "Scripts\n\n Downloaded ALL\n Sensor Updates\n  " + \
            "    OK!\n\n" + str(strftime("%b-%d %H:%M:%S"))
            epd.draw_string_at(frame_black,1,1,str(message_text),font1,1)
            os.system("sudo bash /home/ink/update_script.sh")
            epd.display_frame(frame_black, frame_red)
            key_hit1 = 0

        timer_hit = 0

    elif key2state == False:
        if key_hit2 == 0:
            print("Key2 Op: Remote Sensor Check")
            get_sensor_info()
            key_hit2 = key_hit2 + 1

        elif key_hit2 == 1:
            print("Key3 Op: Download Sensors Pri SQLite Database")
            download_sensor_files()
            key_hit2 = 0

        timer_hit = 0

    elif key3state == False:
        upgrade_message = 0
        if key_hit3 == 0:
            print("Key3 Op:1 Upgrade Sensors")
            upgrade_sensor_progs()
            key_hit3 = key_hit3 + 1

        elif key_hit3 == 1:
            print("Key3 Op:2 reboot Remote Sensors")
            reboot_sensors()
            key_hit3 = 0

        timer_hit = 0

    elif key4state == False:
        print('Shuting Down Local System')
        os.system("sudo shutdown -h now")

    sleep(0.2)