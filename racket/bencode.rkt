#!/usr/bin/env racket

#lang racket


;-----------------------------------------
;                Decoding
;-----------------------------------------

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

;(define torrent-data (file->bytes "test.torrent"))
;(define torrent-data #"d2:\316\273i1337ee")
;(decode-bencoded torrent-data)

;------------------------------------------
;                 Encoding
;------------------------------------------

(define (encode-int i)
  (bytes-append (bytes-append #"i" (string->bytes/utf-8 (number->string i))) #"e"))

(define (encode-string s)
  (define byte-s
    (cond
      [(string? s) (string->bytes/utf-8 s)]
      [else s]))
  (define len-str (number->string (bytes-length byte-s)))
  (bytes-append (bytes-append (string->bytes/utf-8 len-str) #":") byte-s))

(define (recurse-encode-items items)
  (if (null? items)
    #""
    (bytes-append
      (encode-next-item (first items))
      (recurse-encode-items (rest items)))))

(define (encode-list l)
  (bytes-append #"l" (bytes-append (recurse-encode-items l) #"e")))

; expects '((a b) (c d) (e f))
; returns '(a b c d e f)
(define (zip-items items)
    (if (null? items)
      empty
      (cons (car (first items))
            (cons (cdr (first items))
                  (zip-items (rest items))))))

(define (encode-dict d)
    (define sorted-items
      (sort (hash->list d)
            (lambda (x y) (string<? (car x) (car y)))))
    (define zipped-items (zip-items sorted-items))
    (bytes-append #"d" (bytes-append (recurse-encode-items zipped-items) #"e")))

(define (encode-next-item item)
  (cond
    [(integer? item) (encode-int item)]
    [(string? item) (encode-string item)]
    [(bytes? item) (encode-string item)]
    [(list? item) (encode-list item)]
    [(hash? item) (encode-dict item)]
    [else (raise (format "Cannot encode type 'wat'"))]))


;(encode-next-item -32)
;(encode-next-item "hello")
;(encode-next-item #"\316\273")
;(encode-next-item '(1 2))
;(encode-next-item #hash((#"a" . 1337)))

;-----------------------------------------
;     Functions You Should Care About
;-----------------------------------------

(provide bencode-encode)
(provide decode-bencoded)

(define (bencode-encode obj)
  (encode-next-item obj))

(define (decode-bencoded data)
  (define port (open-input-bytes data))
  (decode-next-item port))

