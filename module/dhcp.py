#encoding=utf-8
__author__ = 'liu'

import socket
import struct
from collections import defaultdict
from time import time
import threading

class OutOfLeasesError(Exception):
    pass

class DHCPD:
    def __init__(self):

        self.dhcpd = True
        self.pxe = False
        self.ip = '192.168.137.1'
        self.port = 67
        self.offer_from = '192.168.137.101'
        self.offer_to = '192.168.137.200'
        self.subnet_mask = '255.255.255.0'
        self.router = '192.168.137.1'
        self.dns_server = ['114.114.114.114']
        self.broadcast = '<broadcast>'

        self.file_server = '192.168.239.200'
        self.file_name = 'uefi/ipxe.efi'

        self.magic = struct.pack('!I', 0x63825363)  # magic cookie

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # key is MAC
        self.leases = defaultdict(lambda: {'ip': '', 'expire': 0})

    def next_ip(self):

        # e.g '192.168.1.1' to 3232235777
        encode = lambda x: struct.unpack('!I', socket.inet_aton(x))[0]

        # e.g 3232235777 to '192.168.1.1'
        decode = lambda x: socket.inet_ntoa(struct.pack('!I', x))

        from_host = encode(self.offer_from)
        to_host = encode(self.offer_to)

        # pull out already leased IPs
        leased = [self.leases[i]['ip'] for i in self.leases
                if self.leases[i]['expire'] > time()]

        # convert to 32-bit int
        leased = list(map(encode, leased))

        # loop through, make sure not already leased and not in form X.Y.Z.0
        for offset in range(to_host - from_host):
            if (from_host + offset) % 256 and from_host + offset not in leased:
                return decode(from_host + offset)
        raise OutOfLeasesError('Ran out of IP addresses to lease!')

    def tlv_encode(self, tag, value):
        '''Encode a TLV option.'''
        return struct.pack('BB', tag, len(value)) + value

    def tlv_parse(self, raw):
        '''Parse a string of TLV-encoded options.'''
        ret = {}
        while(raw):
            [tag] = struct.unpack('B', raw[0])
            if tag == 0: # padding
                raw = raw[1:]
                continue
            if tag == 255: # end marker
                break
            [length] = struct.unpack('B', raw[1])
            value = raw[2:2 + length]
            raw = raw[2 + length:]
            if tag in ret:
                ret[tag].append(value)
            else:
                ret[tag] = [value]
        return ret

    def get_mac(self, mac):
        return ':'.join([hex(x)[2:].zfill(2) for x in struct.unpack('BBBBBB', mac)]).upper()

    def craft_header(self, message):
        '''This method crafts the DHCP header using parts of the message.'''
        xid, flags, yiaddr, giaddr, chaddr = struct.unpack('!4x4s2x2s4x4s4x4s16s', message[:44])
        client_mac = chaddr[:6]
        response =  struct.pack('!BBBB4s', 2, 1, 6, 0, xid)

        response += struct.pack('!HHI', 0, 0, 0)

        if self.leases[client_mac]['ip']: # ACK
            offer = self.leases[client_mac]['ip']
            print(('ack_ip:'+offer))
        else: # OFFER
            offer = self.next_ip()
            self.leases[client_mac]['ip'] = offer
            self.leases[client_mac]['expire'] = time() + 86400
            print(('offer_ip:'+offer))
        response += socket.inet_aton(offer) # yiaddr
        response += socket.inet_aton(self.file_server)  # siaddr
        response += socket.inet_aton('0.0.0.0') # giaddr
        response += chaddr # chaddr

        response += chr(0) * 64
        response += chr(0) * 128

        response += self.magic

        return (client_mac, response)

    def craft_options(self, opt53, client_mac):
        response = self.tlv_encode(53, chr(opt53)) # message type, OFFER
        response += self.tlv_encode(54, socket.inet_aton(self.ip)) # DHCP Server
        subnet_mask = self.subnet_mask
        response += self.tlv_encode(1, socket.inet_aton(subnet_mask)) # subnet mask
        router = self.router
        response += self.tlv_encode(3, socket.inet_aton(router)) # router
        dns_server = self.dns_server
        dns_server = ''.join([socket.inet_aton(i) for i in dns_server])
        response += self.tlv_encode(6, dns_server)
        response += self.tlv_encode(51, struct.pack('!I', 86400)) # lease time

        if self.pxe:
            response += self.tlv_encode(66, self.file_server.encode('utf8'))
            response += self.tlv_encode(67, self.file_name + chr(0))


        response += '\xff'
        return response

    def dhcp_offer(self, message):
        '''This method responds to DHCP discovery with offer.'''
        client_mac, header_response = self.craft_header(message)
        options_response = self.craft_options(2, client_mac) # DHCPOFFER
        response = header_response + options_response
        self.sock.sendto(response, (self.broadcast, 68))

    def dhcp_ack(self, message):
        '''This method responds to DHCP request with acknowledge.'''
        client_mac, header_response = self.craft_header(message)
        options_response = self.craft_options(5, client_mac) # DHCPACK
        response = header_response + options_response
        self.sock.sendto(response, (self.broadcast, 68))

    def listen(self):
        '''Main listen loop.'''
        while self.dhcpd:
            message, address = self.sock.recvfrom(1024)
            [client_mac] = struct.unpack('!28x6s', message[:34])
            self.leases[client_mac]['options'] = self.tlv_parse(message[240:])
            type = ord(self.leases[client_mac]['options'][53][0])
            if type == 1:
                self.dhcp_offer(message)
            elif type == 3 and address[0] == '0.0.0.0' :
                self.dhcp_ack(message)

    def start_dhcpd(self):
        self.dhcpd = True
        self.sock.bind((self.ip, self.port))
        listen = threading.Thread(target = self.listen, daemon=True)
        listen.start()

    def stop_dhcpd(self):
        self.dhcpd = False