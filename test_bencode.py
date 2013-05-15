#!/usr/bin/env python
import sys

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
        marker = bencoded_data[0]
        if marker == "e":
            bencoded_data = bencoded_data[1:]
            return bencoded_data, lst
        elif marker in "123456789":
            bencoded_data, s = decode_string(bencoded_data)
            lst.append(s)
        elif marker == "i":
            bencoded_data, i = decode_int(bencoded_data)
            lst.append(i)
        elif marker == "d":
            bencoded_data, d = decode_dict(bencoded_data)
            lst.append(d)
        elif marker == "l":
            bencoded_data, l = decode_list(bencoded_data)
            lst.append(l)

def decode_dict(bencoded_data):
    bencoded_data = bencoded_data[1:]
    key = None
    dictionary = {}

    while 1:
        marker = bencoded_data[0]
        if marker == "e":
            bencoded_data = bencoded_data[1:]
            return bencoded_data, dictionary
        elif marker in "123456789":
            bencoded_data, s = decode_string(bencoded_data)
            if key == None:
                key = s
            else:
                dictionary[key] = s
                key = None
        elif marker == "i":
            bencoded_data, i = decode_int(bencoded_data)
            if key == None:
                print "INTEGER KEY IS BAAAAAD"
            else:
                dictionary[key] = i
                key = None
        elif marker == "d":
            bencoded_data, d = decode_dict(bencoded_data)
            if key == None:
                print "DICT KEY IS BAAAAAD"
            else:
                dictionary[key] = d
                key = None
        elif marker == "l":
            bencoded_data, l = decode_list(bencoded_data)
            if key == None:
                print "LIST KEY IS BAAAAAD"
            else:
                dictionary[key] = l
                key = None
        else:
            print "Unknown marker. Bailing"

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
        print "Unknown token '%s'. Bailing." % marker
        sys.exit(1)

    return bencoded_data, marker, token

def decode(bencoded_data):
    marker = bencoded_data[0]
    if marker == "i":
        bencoded_data, item = decode_int(bencoded_data)
    elif marker in "123456789":
        bencoded_data, item = decode_string(bencoded_data)
    elif marker == "l":
        bencoded_data, item = decode_list(bencoded_data)
    elif marker == "d":
        bencoded_data, item = decode_dict(bencoded_data)
    else:
        print "Unknown marker '%s', bailing." % marker
        return None

    return item

#with open("test.torrent", "r") as f:
#    s = f.read()

print decode("l13:Hello, world!i1337ed3:key5:value3:inti5e4:dictd4:dkey6:dvalueeel5:item15:item25:item3ee")
print decode("d2:k12:v12:k2d3:dk13:dv14:listl5:item15:item2d4:ldk14:ldv1eeee")

