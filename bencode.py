#!/usr/bin/env python

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
                    raise TypeError("Bad key type! (%s)" % marker)
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
        raise TypeError("Unknown marker '%s'." % marker)

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
            raise TypeError("Dictionary keys must be strings, not '%s'" % type(k))

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
    elif type(obj) == list or type(obj) == tuple:
        return _encode_list(obj)
    else:
        raise TypeError("Unsupported type %s." % type(obj))

#-----------------------------------------
#              main() stuff
#-----------------------------------------

if __name__ == "__main__":
    import sys
    with open(sys.argv[1], "r") as f:
        s = f.read().rstrip()

    decoded_obj = decode(s)
    encoded_obj = encode(decoded_obj)

    print "Testing %s..." % sys.argv[1],
    if s == encoded_obj:
        print "Success, reencoded data matched original."
    else:
        print "Failed"
        ok = True
        for (a, b) in zip(repr(s), repr(encoded_obj)):
            if a != b:
                print "!!![", a, b, "] "
                sys.exit()
            else:
                print "[", a, b, "] ",



