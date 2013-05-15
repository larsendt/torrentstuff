#!/usr/bin/env python

import bencode

class TorrentFile(object):
    def __init__(self, path):
        with open(path, "r") as f:
            data = f.read()

        self._raw = bencode.decode(data)
        self._announce = self._raw["announce"]
        self._name = self._raw["info"]["name"]
        self._piece_length = self._raw["info"]["piece length"]
        self._length = self._raw["info"]["length"]
        self._hash_size = hs = 20
        pcs = self._raw["info"]["pieces"]
        self._pieces = [pcs[i*hs:(i+1)*hs] for i in range(len(pcs)/hs)]
        self._files = self._raw["info"].get("files", {})

    def raw(self):
        return self._raw

    def announce(self):
        return self._announce

    def name(self):
        return self._name

    def piece_length(self):
        return self._piece_length

    def length(self):
        return self._length

    def files(self):
        return self._files

    def pieces(self):
        return self._pieces


if __name__ == "__main__":
    tf = TorrentFile("test.torrent")
    print tf.piece_length(), "*", len(tf.pieces())
    print len(tf.pieces()) * tf.piece_length()
    print tf.length()
    print tf.name()
    print tf.announce()



