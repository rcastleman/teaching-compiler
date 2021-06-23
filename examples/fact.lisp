
; fact computes the factorial of n
(def (fact n)
  (if (= n 0)
    1
    (* n (fact (sub1 n))))) 

(print (fact 5))
