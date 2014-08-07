;; Generate CL_UNITS
(format T
        "CL_UNITS = {~%~{~{    ~D: \"~A\"~},~%~}}~2%"
        (LOOP
          for i from 3 to 63 by 3
          collecting `(,i ,(subseq (format NIL "~R" (expt 10 i)) 4))))

;; Generate CL_TEENS
(format T
        "CL_TEENS = {~%~{~{    ~D: \"~R\"~},~%~}}~2%"
        (LOOP
          for i from 10 to 19
          collecting `(,i ,i)))

;; Generate CL_TEENS_TH
(format T
        "CL_TEENS_TH = {~%~{~{    ~D: \"~:R\"~},~%~}}~2%"
        (LOOP
          for i from 10 to 19
          collecting `(,i ,i)))

;; Generate CL_TENS
(format T
        "CL_TENS = {~%~{~{    ~D: \"~R\"~},~%~}}~2%"
        (LOOP
          for i from 10 to 90 by 10
          collecting `(,(/ i 10) ,i)))

;; Generate CL_TENS_TH
(format T
        "CL_TENS_TH = {~%~{~{    ~D: \"~:R\"~},~%~}}~2%"
        (LOOP
          for i from 10 to 90 by 10
          collecting `(,(/ i 10) ,i)))

;; Generate CL_DIGITS
(format T
        "CL_DIGITS = {~%~{~{    ~D: \"~R\"~},~%~}}~2%"
        (LOOP
          for i from 0 to 9
          collecting `(,i ,i)))

;; Generate CL_DIGITS_TH
(format T
        "CL_DIGITS_TH = {~%~{~{    ~D: \"~:R\"~},~%~}}"
        (LOOP
          for i from 0 to 9
          collecting `(,i ,i)))
