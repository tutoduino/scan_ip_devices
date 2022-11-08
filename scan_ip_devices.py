#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import ipaddress
import subprocess
import threading
import argparse

# Create a thread class for simultaneous ping of all devices in the network range
class MyThread(threading.Thread):
    def __init__(self, host):
        threading.Thread.__init__(self)
        self.host = host
        self.myres = None
    def run(self):
        # Call the ping process (count = 2, timeout = 1sec)
        if subprocess.call(['ping', '-c2', '-W1', str(self.host)], stdout=subprocess.DEVNULL) == 0:
            try:
                # Get the hostname of the device that replies to ping
                hostname = socket.gethostbyaddr(str(self.host))[0]
            except socket.herror:
                hostname = '**'
            self.myres = hostname
            
# Thread list is created to store thread results and avoid simultaneous printing
threads = []

def checkArgs():
    # Parse the arguments to get the CIDR (CIDR addressing scheme, e.g. 192.168.1.0/24)
    parser = argparse.ArgumentParser(description='Network scan tool by Herl.')
    parser.add_argument("--cidr",default="192.168.1.0/24", help="e.g. 192.168.1.0/24")
    args=parser.parse_args()
    # check the validity of CIDR
    cidr = args.cidr.split("/")
    if len(cidr) != 2:
        print("Incorrect CIDR")
        exit()
    ip_addr = cidr[0].split(".")
    if len(ip_addr) != 4:
        print("Incorrect CIDR")
        exit()
    if ((not 0 <= int(ip_addr[0]) <= 255) \
        or (not 0 <= int(ip_addr[1]) <= 255) \
            or (not 0 <= int(ip_addr[2]) <= 255) \
                or (not 0 <= int(ip_addr[3]) <= 255)):
        print("Incorrect CIDR")
        exit() 
    if (not 0 <= int(cidr[1]) <= 32):
        print("Incorrect CIDR")
        exit()
        
    return args.cidr
               
if __name__ == '__main__':
    try:
        # Check arguments given in parameters
        cidr = checkArgs()
        
        # Get network range as a list
        my_network = ipaddress.ip_network(cidr)
        # Loop on all devices of the network range
        for my_host in my_network.hosts():
            # Create a thread for pinging the device and add the thread to the end of the thread list
            threads.append(MyThread(my_host))
            # Start the previously created thread
            threads[-1].start()
        # Wait for all the threads to end and print results    
        for thread in threads:
            # Wait the end of the run function
            thread.join()
            if thread.myres != None:
               print("host {} ({}) is up".format(thread.host, thread.myres))
    except ValueError:
        print("ValueError exception raised")
