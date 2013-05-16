#!/usr/bin/env racket

#lang racket

(define (read-until-char port char)
  (define new-char (integer->char (read-byte port)))
  (cond
    [(eof-object? new-char) (raise "character not found")]
    [(char=? new-char char) (string new-char)]
    [else (string-append
            (string new-char)
            (read-until-char port char))]))

(define (decode-int port)
  (define data (read-until-char port #\e))
  (string->number
    (substring data 1 (sub1 (string-length data)))))

(define (decode-string port)
  (define len-str (read-until-char port #\:))
  (define len
    (string->number (substring
                      len-str
                      0
                      (sub1 (string-length len-str)))))
  (read-bytes len port))

(define (decode-list port)
  (read-char port) ; drop the 'l'
  (define (recurse-decode-list port)
    (define item (decode-next-item port))
    (cond
      [(char=? (peek-char port) #\e) (read-char port) (cons item empty)]
      [else (cons item (recurse-decode-list port))]))
  (recurse-decode-list port))

(define (decode-dict port)
  (read-char port) ; drop the 'd'
  (define data-dict (make-hash))
  (define (recurse-decode-dict port key)
    (define marker (peek-char port))
    (cond
      [(char=? marker #\e) #f] ; WARNING: if key is not #f, this will silently ignore the error
      [(equal? key #f)
       (recurse-decode-dict port (decode-next-item port))]
      [else (hash-set! data-dict key (decode-next-item port))
            (recurse-decode-dict port #f)]))
  (recurse-decode-dict port #f)
  data-dict)

(define (decode-next-item port)
  (define marker (peek-char port))
  (cond
    [(char=? marker #\i) (decode-int port)]
    [(char=? marker #\l) (decode-list port)]
    [(char=? marker #\d) (decode-dict port)]
    [(number? (string->number (string marker))) (decode-string port)]
    [else (raise (format "Unknown marker '~v'." marker))]))

(define (decode-bencoded data)
  (define port (open-input-bytes data))
  (decode-next-item port))

(define torrent-data (file->bytes "test.torrent"))
;(define torrent-data #"d2:\316\273i1337ee")
(decode-bencoded torrent-data)
