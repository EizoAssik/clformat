# clformat
==========

A Python implementation of the **format** function in Common Lisp.

The function itself just depends on builtins, the **str** module and the **itertools** module.

As the format in Common Lisp used a complex rules (a powerful DSL, acctually) to format a sting, it's not that easy to reimplement a Python fork elegantly for me, so any help will be greatly appreciated.

## Usage

The generated single-file release contains all the stuff. Just

'''Python
from clformat import clformat
'''

and try it.

