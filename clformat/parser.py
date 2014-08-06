#encoding=utf-8
"""
The one-pass parser that parsers the control string,
and generate the finally callable object to format
the given arguments.
"""

from .directives import combine_atoms, make_fn_obj
from .directives import ArgFn, StatusFn, IterFn

#############
# String Contents & Flags
#############
CURRENT_ARG_COUNT = 'CURRENT_ARG_COUNT'
CURRENT_KWARG_COUNT = 'CURRENT_KWARG_COUNT'
ITER_STACK = 'ITER_STACK'
COMMON_BUFFER = 'COMMON_BUFFER'
OPTION_BUFFER = 'OPTION_BUFFER'
ATOM_DEST = 'ATOM_DEST'
CASE_SENSITIVE = 'CASE_SENSITIVE'


############
# Parser Flags
############

class Flag(object):
    def __init__(self, description):
        self.description = description


GO_TO_LAST_ITER = Flag('GO TO LAST ITER')
GO_UPWARD = Flag('GO UPWARD')


###########
# The parser
###########


def parse_ctrl(ctrl):
    """
    Here, I'm trying to build a one-pass parser to transform the
    given control string into a function, like:
        control_func([*args, [**kwargs]])
    who's finally return value is the formatted sting.

    The parser has 3 steps in the main loop :
        1) initialize the status, `next_action`, `dest`, etc.
        2) execute the main loop, as:
            a. call `next_action` with 2 arguments, the current character
               of the control string and the status of the parser;
            b. handle the result of the `next_action`,
            c. again if the control string is not ended.
        3) combine the atoms to make the final callable, and return it.

    The `next_action` should ALWAYS return 2 values, retval and
    the next value of next value. There're 4 possible type of retval:

        1) the retval is None, means the new `next_action` is waiting
           for more characters of the current dirctive/text now;
        2) the retval is an Exception, and parse_ctrl will just raise it;
        3) the retval is an Fn-Object or a str, and the retval will be
           append to atoms;
        4) the retval is a parser flag, and the parser will execute some
           extra operations to change the status of the parser, or change
           the `dest` to handle loops in the control string.

    Anyway, the `next_action` should NEVER raise a exception, but return
    it as the retval.
    """
    next_action = read
    atoms = []
    status = {CURRENT_ARG_COUNT: 0,
              CURRENT_KWARG_COUNT: 0,
              ITER_STACK: [],
              COMMON_BUFFER: [],
              OPTION_BUFFER: [],
              ATOM_DEST: atoms,
              CASE_SENSITIVE: True}
    dest = atoms
    for c in ctrl:
        retval, next_action = next_action(c, status)
        if isinstance(retval, (str, ArgFn, StatusFn)):
            dest.append(retval)
        elif isinstance(retval, Exception):
            raise retval
        elif retval is GO_TO_LAST_ITER:
            if len(status[ITER_STACK]) > 0:
                dest = status[ITER_STACK][-1]
            else:
                raise IndexError('No frame in iter stack to handle.')
        elif retval is GO_UPWARD:
            if len(status[ITER_STACK]) is 1:
                dest = atoms
            else:
                dest = status[ITER_STACK][-2]
            # Now get the last frame of the iter-stack
            iter_info = status[ITER_STACK].pop()
            # Reset the arg counter
            status[CURRENT_ARG_COUNT] = iter_info[0]['index'] + 1
            # and make a IterFn instance with this frame.
            dest.append(IterFn(atoms=iter_info[1:],
                               index=iter_info[0]['index']))
        elif retval is None:
            continue
        else:
            raise TypeError('Got a {} when parsing control string.'
                            '<class \'Fn\'> excepted.'
                            .format(type(retval)))
    # check for remaining characters
    if status[COMMON_BUFFER]:
        atoms.append(''.join(status[COMMON_BUFFER]))
        status[COMMON_BUFFER].clear()
    if status[OPTION_BUFFER]:
        raise SyntaxError('Non-terminated control string.'
                          'Remaining: {}'.format(status[OPTION_BUFFER]))
    return combine_atoms(atoms)


def read(c: str, status: dict):
    """
    The reader to handle plain text.
    This function will simply append current character into the
    status[COMMON_BUFFER], until meet '~'.
    """
    if c == '~':
        if len(status[COMMON_BUFFER]) > 0:
            _buffer = ''.join(status[COMMON_BUFFER])
            status[COMMON_BUFFER].clear()
            return _buffer, read_tilde
        else:
            return None, read_tilde
    else:
        status[COMMON_BUFFER].append(c)
        return None, read


def read_tilde(c: str, status: dict):
    """
    When meet tildes, the program comes to a big switch.
    """
    escape = {'~': '~',
              '%': '\n',
              '|': '\f'}
    if not status[CASE_SENSITIVE]:
        c = c.upper()
    # handle escaped characters, supporting counts
    if c in escape:
        count = 1
        if status[OPTION_BUFFER]:
            try:
                opt_count = int(''.join(status[OPTION_BUFFER]))
                if opt_count < 0:
                    raise ValueError()
            except:
                raise SyntaxError()
            else:
                count = opt_count
        chars = escape[c] * count
        status[OPTION_BUFFER].clear()
        status[COMMON_BUFFER].append(chars)
        return None, read
    # handle prefixing introductions
    elif c in {':', '@'} or c.isdigit():
        status[OPTION_BUFFER].append(c)
        return None, read_tilde
    # handle directives
    elif c in {'A', 'C', 'W'}:
        index = status[CURRENT_ARG_COUNT]
        status[CURRENT_ARG_COUNT] += 1
        options = ''.join(status[OPTION_BUFFER])
        status[OPTION_BUFFER].clear()
        return make_fn_obj(directive=c, index=index, options=options), read
    elif c in {'&'}:
        options = ''.join(status[OPTION_BUFFER])
        status[OPTION_BUFFER].clear()
        return make_fn_obj(directive=c, options=options), read
    elif c == '$':
        pass
    elif c == '{':
        status[ITER_STACK].append([{'index': status[CURRENT_ARG_COUNT],
                                    'depth': len(status[ITER_STACK])}])
        # Restart the counter for this frame.
        status[CURRENT_ARG_COUNT] = 0
        return GO_TO_LAST_ITER, read
    elif c == '}':
        return GO_UPWARD, read
    else:
        return SyntaxError('clformat cannot parse the directive "~{}{}".'
                           .format(''.join(status[OPTION_BUFFER]), c)), read
