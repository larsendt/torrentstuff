#lang racket

; not sure this is the right thing to do
(define bencode-data (make-parameter ""))

(define (find-character str char)
  (define orig-length (string-length str))
  (define (recurse-find-char str char pos)
    (cond
      [(string=? char (substring str 0 1)) pos]
      [(>= pos orig-length) -1]
      [else (recurse-find-char (substring str 1) char (add1 pos))]))
  (recurse-find-char str char 0))

(define (decode-next-item data)
  (bencode-data data)
  (define marker (substring data 0 1))
  (cond
    [(string=? marker "i") (decode-int data)]
    [(string=? marker "l") (decode-list data)]
    [(number? (string->number marker)) (decode-string data)]
    [else #f]))

(define (decode-int data)
  (define end (find-character data "e"))
  (bencode-data (substring data (add1 end)))
  (string->number (substring data 1 end)))

(define (decode-string data)
  (define delim (find-character data ":"))
  (define strlen (string->number (substring data 0 delim)))
  (bencode-data (substring data (+ strlen (add1 delim))))
  (substring data (add1 delim) (+ strlen (add1 delim))))

; this is not pretty
(define (decode-list data)
  (define (recurse-list-items data)
    (define item (decode-next-item data))
    ; if item is #f, we've hit the end of the list, so
    ; strip off the 'e'
    (if (equal? item #f)
      (bencode-data (substring (bencode-data) 1))
      #f)
    (cond
      [(equal? item #f) empty]
      [else (cons item (recurse-list-items (bencode-data)))]))
  (recurse-list-items (substring data 1)))

(decode-next-item "i1337e")
(decode-next-item "12:dis a string")
(decode-next-item "l1:a1:bl2:aa2:bbe1:ce")
