#!/usr/bin/env racket
#lang racket

(require racket/udp)
(require openssl/sha1)
(require "bencode.rkt")

(define (new-160-bit-id [seed (current-seconds)])
  (random-seed seed)
  (define id (make-bytes 20))
  (for ([i (in-range 20)])
       (bytes-set! id i(random 256)))
  id)

(define current-node-id (make-parameter (new-160-bit-id)))

(define (dht-query socket msg-dict)
  (define msg (bencode-encode msg-dict))
  (define response-buffer (make-bytes 4096))
  (udp-send socket msg)
  (define-values
    (bytes-received remote-host remote-port)
    (udp-receive! socket response-buffer 0 4096))
  (define response (decode-bencoded (subbytes response-buffer 0 bytes-received)))
  (values remote-host remote-port response))

(define (split-node-ids node-bytes)
  (define node-bytes-port (open-input-bytes node-bytes))
  (define (recurse-split port)
    (define next-id (read-bytes 20 port))
    (if (eof-object? next-id)
      empty
      (cons next-id (recurse-split port))))
  (recurse-split node-bytes-port))

(define (send-ping socket)
  (dht-query socket `#hash(("t" . "01")
                           ("y" . "q")
                           ("q" . "ping")
                           ("a" . #hash(("id" . ,(current-node-id)))))))

(define (get-peers socket info-hash)
  (define msg `#hash(("t" . "02")
                     ("y" . "q" )
                     ("q" . "get_peers")
                     ("a" . #hash(("id" . ,(current-node-id))
                                  ("info_hash" . ,info-hash)))))
  (dht-query socket msg))

(define (find-node socket target-id)
  (define msg `#hash(("t" . "03")
                     ("y" . "q")
                     ("q" . "find_node")
                     ("a" . #hash(("id" . ,(current-node-id))
                                  ("target" . ,target-id)))))
  (dht-query socket msg))

(define bootstrap-host "router.bittorrent.com")
(define bootstrap-port 6881)
(define socket (udp-open-socket))
(udp-connect! socket bootstrap-host bootstrap-port)

(define info-hash (new-160-bit-id 1337))
(printf "This Node ID: ~v~n" (bytes->hex-string (current-node-id)))
(printf "New Hash ID: ~v~n" (bytes->hex-string info-hash))
(printf "Pinging ~a:~v~n" bootstrap-host bootstrap-port)

(define-values (host port ping-response) (send-ping socket))

(define remote-id (bytes->hex-string (hash-ref (hash-ref ping-response #"r") #"id")))
(printf "Remote host ~a:~v identifies as ~v~n" host port remote-id)

(printf "Requesting nodes for info-hash ~v~n" (bytes->hex-string info-hash))
(define-values (host2 port2 peers-response) (get-peers socket info-hash))
(define node-id-list (split-node-ids (hash-ref (hash-ref peers-response #"r") #"nodes")))
(printf "Got ~v nodes~n" (length node-id-list))

(define first-node (first node-id-list))
(printf "Requesting contact info for node ~v~n" (bytes->hex-string first-node))
(define-values (host3 port3 node-response) (find-node socket first-node))
(define nodes (hash-ref (hash-ref node-response #"r") #"nodes"))

