#!/usr/bin/env python
import sys

#-------------------------------------------------
#      The Functions You Should Care About
#-------------------------------------------------

def decode(bencoded_data):
    """Decode a Bencode string into a Python data structure."""
    return _decode_next_token(bencoded_data)[2]

def encode(obj):
    """Encode a python object (dict, list, int, string) in the Bencode format. Accepts nested structures."""
    return _encode_next_object(obj)

#--------------------------------------------------
#                   Decoding
#--------------------------------------------------

def _decode_string(bencoded_data):
    delim = bencoded_data.find(":")
    sz = int(bencoded_data[:delim])
    s = bencoded_data[delim+1:sz+delim+1]
    bencoded_data = bencoded_data[delim+sz+1:]
    return bencoded_data, s


def _decode_int(bencoded_data):
    end = bencoded_data.find("e")
    i = int(bencoded_data[1:end])
    bencoded_data = bencoded_data[end+1:]
    return bencoded_data, i


def _decode_list(bencoded_data):
    bencoded_data = bencoded_data[1:]
    lst = []

    while 1:
        if bencoded_data[0] == "e":
            break
        else:
            bencoded_data, marker, token = _decode_next_token(bencoded_data)
            lst.append(token)

    return bencoded_data[1:], lst


def _decode_dict(bencoded_data):
    bencoded_data = bencoded_data[1:]
    key = None
    dictionary = {}

    while 1:
        if bencoded_data[0] == "e":
            break
        else:
            bencoded_data, marker, token = _decode_next_token(bencoded_data)
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


def _decode_next_token(bencoded_data):
    marker = bencoded_data[0]

    if marker in "123456789":
        bencoded_data, token = _decode_string(bencoded_data)
    elif marker == "i":
        bencoded_data, token = _decode_int(bencoded_data)
    elif marker == "d":
        bencoded_data, token = _decode_dict(bencoded_data)
    elif marker == "l":
        bencoded_data, token = _decode_list(bencoded_data)
    else:
        print "Unknown marker '%s'. Bailing." % marker
        sys.exit(1)

    return bencoded_data, marker, token


#--------------------------------------------------
#                   Encoding
#--------------------------------------------------

def _encode_int(i):
    return "i" + str(i) + "e"


def _encode_string(s):
    return "%d:%s" % (len(s), s)


def _encode_dict(d):
    bencoded_data = ""
    kvpairs = sorted(d.items(), key=lambda x: x[0])

    for k, v in kvpairs:
        if type(k) == str:
            bencoded_data += _encode_next_object(k)
            bencoded_data += _encode_next_object(v)
        else:
            print "Dictionary keys must be strings, not '%s'" % type(k)

    return "d" + bencoded_data + "e"


def _encode_list(l):
    bencoded_data = ""
    for item in l:
        bencoded_data += _encode_next_object(item)

    return "l" + bencoded_data + "e"


def _encode_next_object(obj):
    if type(obj) == int:
        return _encode_int(obj)
    elif type(obj) == str:
        return _encode_string(obj)
    elif type(obj) == dict:
        return _encode_dict(obj)
    elif type(obj) == list:
        return _encode_list(obj)
    else:
        print "Unsupported type %s. Bailing." % type(obj)
        sys.exit(1)


#-----------------------------------------
#              main() stuff
#-----------------------------------------

if __name__ == "__main__":
    with open("test.torrent", "r") as f:
        s = f.read()

    decoded_obj = decode(s)
    encoded_obj = encode(decoded_obj)

    print "Testing test.torrent...",
    if s == encoded_obj:
        print "Success, reencoded data matched original."
    else:
        print "Failed"
        print "Expected:", s
        print "Got:", encoded_obj


