#!/usr/bin/env racket

#lang racket

(require openssl/sha1)
(require racket/cmdline)
(require "bencode.rkt")

(define (split-into-pieces data piece-length)
  (if (<= (bytes-length data) piece-length)
    (cons data empty)
    (cons
      (subbytes data 0 piece-length)
      (split-into-pieces (subbytes data piece-length) piece-length))))

(define current-piece-number (make-parameter 0))

(define (hashed-file-pieces file-port piece-length)
  (current-piece-number (add1 (current-piece-number)))
  (if (= 0 (modulo (current-piece-number) 100))
    (printf "~v pieces encoded~n" (current-piece-number))
    #f)
  (define raw-data (read-bytes piece-length file-port))
  (define next-byte (peek-byte file-port))
  (define (make-sha1 data)
    (sha1-bytes (open-input-bytes data)))
  (if (eof-object? next-byte)
    (make-sha1 raw-data)
    (bytes-append (make-sha1 raw-data) (hashed-file-pieces file-port piece-length))))

(define name (make-parameter ""))
(define announce (make-parameter ""))
(define piece-length-str (make-parameter "256"))
(define path (make-parameter ""))

(command-line
  #:program "make-torrent"
  #:once-each
  [("-f" "--file") f "File to seed."
                   (path f)]
  [("-a" "--announce") a "Tracker announce URL."
                       (announce a)]
  [("-p" "--piece-length") p "Piece length in KiB. (Default 256)"
                           (piece-length-str p)]
  [("-n" "--name") n "Name of the torrent. (Default <file>.torrent)"
                   (name n)])

(define tmp1
  (if (= (string-length (path)) 0)
    ((printf "Input filename required [-f]~n") (exit))
    #f))

(define tmp2
  (if (= (string-length (announce)) 0)
    ((printf "Tracker announce URL required [-a]~n") (exit))
    #f))

(define tmp3
  (if (= (string-length (name)) 0)
    (name (string-append (path) ".torrent"))
    #f))

(printf "Creating torrent file: ~v~n" (name))

(define piece-length (* (string->number (piece-length-str)) (expt 2 10)))

(define file-length (file-size (path)))
(define piece-count (add1 (quotient file-length piece-length)))
(printf "Estimated torrent file size: ~v bytes.~n" (* piece-count 20))
(printf "Encoding ~v pieces.~n" piece-count)

(define sha-pieces (hashed-file-pieces (open-input-file (path)) piece-length))

(define info-hash (make-hash))
(hash-set! info-hash "name" (name))
(hash-set! info-hash "piece length" piece-length)
(hash-set! info-hash "length" file-length)
(hash-set! info-hash "path" (path))
(hash-set! info-hash "pieces" sha-pieces)

(define torrent-hash (make-hash))
(hash-set! torrent-hash "announce" (announce))
(hash-set! torrent-hash "info" info-hash)


(define encoded-data (bencode-encode torrent-hash))
(define out (open-output-file (name)
              #:exists 'replace))
(define bytes-written (write-bytes encoded-data out))
(close-output-port out)








