#!/usr/bin/env racket
#lang racket

(require racket/udp)
(require "bencode.rkt")

(define (dht-query socket msg-dict)
  (define msg (bencode-encode msg-dict))
  (define response-buffer (make-bytes 4096))
  (udp-send socket msg)
  (printf "sent query~n")
  (define-values
    (bytes-received remote-host remote-port)
    (udp-receive! socket response-buffer 0 4096))
  (define response (decode-bencoded (subbytes response-buffer 0 bytes-received)))
  (values remote-host remote-port response))

(define (send-ping host port)
  (define socket (udp-open-socket))
  (udp-connect! socket host port)
  (dht-query socket #hash(("t" . "01") ("y" . "q") ("q" . "ping") ("a" . #hash(("id" . "racket"))))))


(send-ping "router.bittorrent.com" 6881)
