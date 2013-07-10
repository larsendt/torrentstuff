#!/usr/bin/env python

import socket
import hashlib
import bencode
import random

def make_id(seed=None):
    if seed is not None:
        random.seed(seed)
    return "".join([chr(random.randint(0, 255)) for i in range(20)])

def id_to_hex_string(id_string):
    hex_str = ""
    for c in id_string:
        i = ord(c)
        hex_str += hex(i % 16)[-1]
        hex_str += hex((i / 16) % 16)[-1]
    return hex_str

CURRENT_ID = make_id()


def dht_query(sock, msg_obj):
    msg_str = bencode.encode(msg_obj)
    sock.send(msg_str)
    response_str, addr = sock.recvfrom(4096)
    return bencode.decode(response_str), addr


def send_ping(sock):
    response = dht_query(sock, {"t":"01",
                                "y":"q",
                                "q":"ping",
                                "a":{"id": CURRENT_ID}})
    return response[0]["r"]["id"]


def get_peers(sock, info_hash):
    response = dht_query(sock, {"t":"02",
                                "y":"q",
                                "q":"get_peers",
                                "a":{"id":CURRENT_ID,
                                     "info_hash":info_hash}})
    peers = []
    peer_string = bytes(response[0]["r"]["nodes"])
    print len(peer_string)
    while peer_string != "":
        peers.append(peer_string[:20])
        peer_string = peer_string[20:]

    return peers



def find_node(sock, target_id):
    return dht_query(sock, {"t":"03",
                            "y":"q",
                            "q":"find_node",
                            "a":{"id":CURRENT_ID,
                                 "target":target_id}})


bootstrap_addr = ("router.bittorrent.com", 6881)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect(bootstrap_addr)

info_hash = make_id(1337)

host_id = send_ping(sock)
print "ping response id:", id_to_hex_string(host_id)

peers = get_peers(sock, info_hash)
print [id_to_hex_string(peer) for peer in peers]
