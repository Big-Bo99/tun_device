#!/usr/bin/python3

import fcntl
import os
import struct
import subprocess
import time

from array import array

TUNSETIFF = 0x400454ca
TUNSETOWNER = TUNSETIFF + 2
IFF_TUN = 0x0001
IFF_TAP = 0x0002
IFF_NO_PI = 0x1000

tun = open('/dev/net/tun', 'r+b', buffering=0)
ifr = struct.pack('16sH', b'tun0', IFF_TUN | IFF_NO_PI)
fcntl.ioctl(tun, TUNSETIFF, ifr)
fcntl.ioctl(tun, TUNSETOWNER, 1000)

subprocess.check_call('ifconfig tun0 192.168.137.1 pointopoint 192.168.137.10 up',
        shell=True)

while True:
    packet = array('B', os.read(tun.fileno(), 2048))

    packet[12:16], packet[16:20] = packet[16:20], packet[12:16]

    if True:
        packet[20] = 0
        packet[22] = 0
        packet[23] = 0
        checksum = 0

        for i in range(20, len(packet), 2):
            half_word = (packet[i] << 8) + (packet[i+1])
            checksum += half_word

        checksum = ~(checksum + 4) & 0xffff
       
        packet[22] = checksum >> 8
        packet[23] = checksum & ((1 << 8) -1)

    os.write(tun.fileno(), bytes(packet))
