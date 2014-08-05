#encoding=utf-8

from itertools import cycle
#############
# String Contents & Flags
#############
CURRENT_ARG_COUNT = 'CURRENT_ARG_COUNT'
CURRENT_KWARG_COUNT = 'CURRENT_KWARG_COUNT'
ITER_STACK = 'ITER_STACK'
COMMON_BUFFER = 'COMMON_BUFFER'
ATOM_DEST = 'ATOM_DEST'
CASE_SENSITIVE = 'CASE_SENSITIVE'

#############
# Fn class that handles the real function
# which will be applied on each args.
#############


class Fn(object):
    """
    All *Fn classes should inherit the Fn class directly or not directly
    Then rewrite its own __call__ method
    """
    def __init__(self, fn, index=None, options=None):
        self.fn = fn
        self.index = index
        self.options = options

    def __call__(self, *args, **kwargs):
        """
        as the __call__ method of object itself looks like:
            __call__(self, *args, **kwargs)
        and I'm not gotta change it, processing `args` needs extra attention.
        """
        return self.fn(*args, **kwargs)


class AnyFn(Fn):
    """
    handle the '~A' directives
    """

    def __init__(self, fn, index=None, options=None):
        super().__init__(fn, index, options)

    def __call__(self, *args, **kwargs):
        if self.index is None:
            return self.fn(args[0])
        return self.fn(args[self.index])


class WriteFn(AnyFn):
    """
    handle the '~W' directives
    just like AnyFn, but this uses repr() rather than fn to
    product a string from the given argument.
    """

    def __init__(self, fn=None, index=None, options=None):
        super().__init__(fn, index, options)

    def __call__(self, *args, **kwargs):
        if self.index is None:
            return repr(args[0])
        return repr(args[self.index])


class KwFn(Fn):
    # TODO try make this compatible with the origin {key} notations
    """
    NOT IMPLEMENTED YET
    """

    def __init__(self, fn, index=None):
        super().__init__(fn, index)

    def __call__(self, *args, **kwargs):
        if self.index:
            return self.fn(args[0])
        return self.fn(kwargs[self.index])


class IterFn(Fn):
    def __init__(self, atoms, index):
        super().__init__(atoms, index)

    def __call__(self, *args, **kwargs):
        # As all the atoms will be called one by one
        # the index is no more meaningful
        # This will use the given *one* arg.
        for atom in self.fn:
            if isinstance(atom, (AnyFn, KwFn)):
                atom.index = None
        pieces = []
        # TODO HANDLE kwargs
        atom_iter = cycle(self.fn)
        args_iter = iter(args[0])
        for atom in atom_iter:
            if isinstance(atom, str):
                pieces.append(atom)
            elif isinstance(atom, Fn):
                try:
                    pieces.append(atom(next(args_iter)))
                except StopIteration:
                    break
            else:
                raise TypeError('Except Fn or str. {} get.'.format(type(atom)))
        return ''.join(pieces)


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
        _clformat([*args, [**kwargs]])
    who's finally return value is the formatted sting.
    """
    next_action = read
    atoms = []
    status = {CURRENT_ARG_COUNT: 0,
              CURRENT_KWARG_COUNT: 0,
              ITER_STACK: [],
              COMMON_BUFFER: [],
              ATOM_DEST: atoms,
              CASE_SENSITIVE: True}
    dest = atoms
    for c in ctrl:
        retval, next_action = next_action(c, status)
        if isinstance(retval, (str, AnyFn, KwFn)):
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
            # Now get the last frame of the iter stack
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
    return _combine_atoms(atoms)


def read(c: str, status: dict):
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
    if not status[CASE_SENSITIVE]:
        c = c.upper()
    if c == '~':
        status[COMMON_BUFFER].append('~')
        return None, read
    elif c == 'A':
        index = status[CURRENT_ARG_COUNT]
        status[CURRENT_ARG_COUNT] += 1
        return AnyFn(fn=lambda x: str(x),
                     index=index), read
    elif c == 'W':
        index = status[CURRENT_ARG_COUNT]
        status[CURRENT_ARG_COUNT] += 1
        return WriteFn(index=index), read
    elif c == '%':
        status[COMMON_BUFFER].append('\n')
        return None, read
    elif c == 'T':
        status[COMMON_BUFFER].append('\t')
        return None, read
    elif c == '{':
        status[ITER_STACK].append([{'index': status[CURRENT_ARG_COUNT],
                                    'depth': len(status[ITER_STACK])}])
        # Restart the counter for this frame.
        status[CURRENT_ARG_COUNT] = 0
        # TODO handle the god damn kwargs here
        return GO_TO_LAST_ITER, read
    elif c == '}':
        return GO_UPWARD, read
    else:
        return SyntaxError('clformat cannot parse ~%c.' % c), read


#################
# Below, functions to make a fn
#################

def _count_atom(atoms: list, find: type):
    counter = 0
    for atom in atoms:
        if isinstance(atom, find):
            counter += 1
    return counter


def _atom_caller(arg, kwargs):
    def __atom_caller(atom: Fn):
        # Both ArgFn and IterFn in this case
        if isinstance(atom, (AnyFn, WriteFn)):
            return atom(*arg)
        elif isinstance(atom, IterFn):
            return atom(*arg)
        elif isinstance(atom, KwFn):
            return atom(**kwargs)
        elif isinstance(atom, str):
            return atom
        else:
            raise TypeError('Error occurred during combing atoms. '
                            'ArgFn/KwFn objects excepted, got {}.'
                            .format(str(type(atom))))

    return __atom_caller


def _combine_atoms(atoms: list):
    _arg_count = _count_atom(atoms, AnyFn) + _count_atom(atoms, IterFn)
    _kwarg_count = _count_atom(atoms, KwFn)

    def __combine_atoms(*args, **kwargs):
        if len(args) != _arg_count:
            raise ValueError("Need {} of args, got {}"
                             .format(_arg_count, len(args)))
        if len(kwargs) != _kwarg_count:
            raise ValueError("Need {} of kwargs, got {}"
                             .format(_kwarg_count, len(kwargs)))
        return ''.join(map(_atom_caller(args, kwargs), atoms))

    return __combine_atoms
