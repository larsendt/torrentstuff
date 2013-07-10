#!/usr/bin/env python

import socket
import hashlib
import bencode
import random
import struct
import sys



def make_id(seed=None):
    if seed is not None:
        random.seed(seed)
    return "".join([chr(random.randint(0, 255)) for i in range(20)])


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
    return dht_query(sock, {"t":"02",
                            "y":"q",
                            "q":"get_peers",
                            "a":{"id":CURRENT_ID,
                                 "info_hash":info_hash}})


def find_node(sock, target_id):
    response = dht_query(sock, {"t":"03",
                                "y":"q",
                                "q":"find_node",
                                "a":{"id":CURRENT_ID,
                                     "target":target_id}})
    print response
    return response


def hex_string_to_id(hex_str):
    id_str = ""
    while hex_str != "":
        byte = hex_str[:2]
        hex_str = hex_str[2:]

        id_str += chr(int(byte, 16))

    return id_str


def id_to_hex_string(id_string):
    hex_str = ""
    for c in id_string:
        i = ord(c)
        hex_str += hex(i % 16)[-1]
        hex_str += hex((i / 16) % 16)[-1]
    return hex_str


def integer_ip_to_string(ip):
    segments = []
    for i in range(4):
        segments.append(str((ip << i) & 0xff))
    return ".".join(segments)


def split_peer_string(peer_string):
    peers = []
    while peer_string != "":
        tmpstring = peer_string[:26]
        peer = peer_string[:20]
        ip = integer_ip_to_string(struct.unpack(">I", peer_string[20:24])[0])
        port = struct.unpack(">H", peer_string[24:26])[0]
        peers.append((peer, ip, port))
        peer_string = peer_string[26:]

    return peers


def id_distance(id1, id2):
    byte_pairs = map(lambda v: (ord(v[0]), ord(v[1])), zip(id1, id2))
    xored_values = map(lambda v: (v[0] ^ v[1]), byte_pairs)
    accum = 0
    for i in range(len(xored_values)):
        accum += xored_values[i] << (8 * (len(xored_values) - i - 1))

    return accum


def resolve_node(node_id):
    bootstrap_addr = ("router.bittorrent.com", 6881)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(bootstrap_addr)
    response = find_node(sock, node_id)[0]
    sock.close()

    peer_pool = []

    if "y" in response and response["y"] == "r" and "nodes" in response["r"]:
        peer_pool += split_peer_string(response["r"]["nodes"])
    else:
        print "Something went wrong!", response
        return None

    while peer_pool != []:
        print "%d peers in the peer pool" % len(peer_pool)
        min_peer = peer_pool[0]
        min_dist = id_distance(min_peer[0], node_id)
        for peer in peer_pool:
            dist = id_distance(peer[0], node_id)
            if dist < min_dist:
                print "New min dist:", dist, peer[1], peer[2]
                min_dist = dist
                min_peer = peer


        print "Querying next peer:", min_peer[1], min_peer[2]
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect((min_peer[1], min_peer[2]))
        print "Connected"
        response = find_node(sock, node_id)[0]
        print "Got response"
        sock.close()

        if "y" in response and response["y"] == "r" and "nodes" in response["r"]:
            peer_pool += split_peer_string(response["r"]["nodes"])
        else:
            print "Something went wrong!", response
            return None


# router.utorrent.com's id
info_hex_string = "27d258e973fef64e6d97b749ac2d3491f70bfe24"
info_hash = hex_string_to_id(info_hex_string)

resolve_node(info_hash)

"""
host_id = send_ping(sock)
print "ping response id:", id_to_hex_string(host_id)

print "searching for:", info_hex_string
peers = find_node(sock, info_hash)[0]["r"]["nodes"]
print split_peer_string(peers)
"""
