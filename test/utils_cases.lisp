;; use this to generate cases for clformat.utils.radix.spell_int
(DOTIMES (c 10)
         (let ((v (random (expt 10 66))))
           (format T
                   "            (~D, \"~R\"),~%"
                   v v)))
