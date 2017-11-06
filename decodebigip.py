#!/usr/bin/env python  
import struct, sys  
ip = sys.argv[1]  
ip = ip[ip.find('=') + 1:]  
a = ip.find('.')  
if a != -1: ip = ip[:a]  
ip = '.'.join(['%i' % ord(c) for c in struct.pack('<I', int(ip))])  
print ip
