
; odd? determines if a number is odd
(def (odd? n)
  (if (= n 0) 0 (even? (sub1 n))))

; even? determines if a number is even
(def (even? n)
  (if (= n 0) 1 (odd? (sub1 n))))

; print-if-odd prints n if it is odd
(def (print-if-odd n)
  (if (odd? n)
    (print n)
    n))

; print-odds-helper prints odd numbers from start to end
(def (print-odds-in-range start end)
  (if (= start end)
    start
    (let (void (print-if-odd start)) 
      (print-odds-in-range (add1 start) end))))

(print-odds-in-range 0 50)
