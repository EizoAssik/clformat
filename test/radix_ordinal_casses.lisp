;; use this to generate cases for clformat.utils.radix.int_english whit ordinal
(DOTIMES (c 10)
         (let ((v (random (expt 10 66))))
           (format T
                   "            (~D, \"~:R\"),~%"
                   v v)))
