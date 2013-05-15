#!/usr/bin/env python
import sys

#--------------------------------------------------
#                   Decoding
#--------------------------------------------------

def decode_string(bencoded_data):
    delim = bencoded_data.find(":")
    sz = int(bencoded_data[:delim])
    s = bencoded_data[delim+1:sz+delim+1]
    bencoded_data = bencoded_data[delim+sz+1:]
    return bencoded_data, s

def decode_int(bencoded_data):
    end = bencoded_data.find("e")
    i = int(bencoded_data[1:end])
    bencoded_data = bencoded_data[end+1:]
    return bencoded_data, i

def decode_list(bencoded_data):
    bencoded_data = bencoded_data[1:]
    lst = []

    while 1:
        if bencoded_data[0] == "e":
            break
        else:
            bencoded_data, marker, token = decode_next_token(bencoded_data)
            lst.append(token)

    return bencoded_data[1:], lst

def decode_dict(bencoded_data):
    bencoded_data = bencoded_data[1:]
    key = None
    dictionary = {}

    while 1:
        if bencoded_data[0] == "e":
            break
        else:
            bencoded_data, marker, token = decode_next_token(bencoded_data)
            if key == None:
                if marker in "123456789":
                    key = token
                else:
                    print "Bad key type! (%s)" % marker
                    sys.exit(1)
            else:
                dictionary[key] = token
                key = None

    return bencoded_data[1:], dictionary

def decode_next_token(bencoded_data):
    marker = bencoded_data[0]

    if marker in "123456789":
        bencoded_data, token = decode_string(bencoded_data)
    elif marker == "i":
        bencoded_data, token = decode_int(bencoded_data)
    elif marker == "d":
        bencoded_data, token = decode_dict(bencoded_data)
    elif marker == "l":
        bencoded_data, token = decode_list(bencoded_data)
    else:
        print "Unknown marker '%s'. Bailing." % marker
        sys.exit(1)

    return bencoded_data, marker, token

def decode(bencoded_data):
    return decode_next_token(bencoded_data)[2]

#--------------------------------------------------
#                   Encoding
#--------------------------------------------------

def encode_int(i):
    return "i" + str(i) + "e"

def encode_string(s):
    return "%d:%s" % (len(s), s)

def encode_dict(d):
    bencoded_data = ""
    kvpairs = sorted(d.items(), key=lambda x: x[0])

    for k, v in kvpairs:
        if type(k) == str:
            bencoded_data += encode_next_object(k)
            bencoded_data += encode_next_object(v)
        else:
            print "Dictionary keys must be strings, not '%s'" % type(k)

    return "d" + bencoded_data + "e"

def encode_list(l):
    bencoded_data = ""
    for item in l:
        bencoded_data += encode_next_object(item)

    return "l" + bencoded_data + "e"

def encode_next_object(obj):
    if type(obj) == int:
        return encode_int(obj)
    elif type(obj) == str:
        return encode_string(obj)
    elif type(obj) == dict:
        return encode_dict(obj)
    elif type(obj) == list:
        return encode_list(obj)
    else:
        print "Unsupported type %s. Bailing." % type(obj)
        sys.exit(1)

def encode(obj):
    return encode_next_object(obj)

with open("test.torrent", "r") as f:
    s = f.read()

decoded_obj = decode(s)
encoded_obj = encode(decoded_obj)

print s == encoded_obj
