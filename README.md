# clformat

CL-format is a Python implementation of the **format** function in Common Lisp.

## About

The function itself just depends on builtins, the **str** module and the **itertools** module.

As the format in Common Lisp used a complex rules (a powerful DSL, acctually) to format a sting, it's not that easy to reimplement a Python fork elegantly for me, so any help will be greatly appreciated.

**NOTICE**:
Only tested in CPython 3.4.1, I'm sorry but clformar cannot works in PyPy3 now. I'll fix this after the function finally works.

## Usage

'''Python
from clformat.fn import clformat
'''

and try it.

# Documention

See CL-format documents [here][doc].

For documentions of the **format** function in Common Lisp, see [here][clhs].

[doc]:  https://github.com/EizoAssik/clformat/blob/master/docs.md
[clhs]: http://www.lispworks.com/documentation/lw51/CLHS/Body/22_c.htm
