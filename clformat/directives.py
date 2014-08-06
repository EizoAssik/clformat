#encoding=utf-8
"""
All the functions & classes is implemented here.
"""
from itertools import cycle
from unicodedata import name
import string


#############
# Fn class that handles the directives
# which will be applied on each argument.
#############


class Fn(object):
    """
    All *Fn classes should inherit the Fn class directly or not directly
    Then rewrite its own __call__ method
    """

    def __init__(self, index=None, options=None):
        # self._fn is never used
        self.index = index
        self.options_str = options

    def __call__(self, *args, **kwargs):
        """
        as the __call__ method of object itself looks like:
            __call__(self, *args, **kwargs)
        and I'm not gotta change it, processing `args` needs extra attention.
        """
        pass

    def init_option(self):
        return self.options_str


class ArgFn(Fn):
    """
    The base class designed to handle the directives
    that only uses positional arguments.
    """

    def __init__(self, index=None, options=None):
        super().__init__(index=index, options=options)

    def __call__(self, *args, **kwargs):
        if self.index is None:
            return self.fn(args[0])
        return self.fn(args[self.index])

    def fn(self, arg):
        pass


class StatusFn(Fn):
    """
    The base class designed to handle the directives
    that only uses current status of the parser, and
    the already formatted pieces, like conditional
    newline.
    """

    def __init__(self, pieces, options):
        super().__init__(options=options)
        self.pieces = pieces

    def __call__(self, *args, **kwargs):
        return self.fn()

    def fn(self):
        pass

    def set_pieces(self, pieces):
        self.pieces = pieces


class IterFn(Fn):
    """
    IterFn is used tu handle the loops in the control string.
    """

    def __init__(self, atoms, index):
        super().__init__(index=index)
        self.atoms = atoms

    def __call__(self, *args, **kwargs):
        """
        As all the atoms will be called one by one
        the index is no more meaningful
        This will use the given *one* arg.
        """
        for atom in self.atoms:
            if isinstance(atom, (ArgFn, KwFn)):
                atom.index = None
        pieces = []
        atom_iter = cycle(self.atoms)
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


class StatusArgFn(ArgFn):
    """
    The base
    """
    pass


class KwFn(Fn):
    # TODO try make this compatible with the origin {key} notations of Python
    """
    The base class designed to handle the directives
    that uses dictionary arguments.
    NOT IMPLEMENTED YET
    """


class AnyFn(ArgFn):
    """
    Handle the '~A' directives.
    """

    def fn(self, arg):
        return str(arg)


class WriteFn(ArgFn):
    """
    handle the '~W' directives.
    just like AnyFn, but this uses repr() rather than fn to
    product a string from the given argument.
    """

    def fn(self, arg):
        return repr(arg)


class DigitFn(ArgFn):
    """
    Handle the '~A' directives.
    """

    def __call__(self, *args, **kwargs):
        pass


class CharFn(ArgFn):
    """
    CharFn is used to handle the '~C' directives.
    As Python uses 'str'
    """
    SPELL_OUT = {
        ' ': 'Space',
        '\t': 'Tab',
        '\n': 'Newline',
        '\b': 'Backspace',
        '\v': 'VTab',
        '\f': 'Page',
        '\r': 'Return',
        '\l': 'Linefeed',
        '\a': 'Rubout'
    }

    def __init__(self, index=None, options=None):
        super().__init__(index=index, options=options)
        self.spelled_out = False
        self.read_back = False
        self.keyboard = False
        self.options = self.init_option()

    def init_option(self):
        if self.options_str is '':
            return None
        elif self.options_str is ':':
            self.spelled_out = True
        elif self.options_str is '@':
            self.read_back = True
        elif self.options_str is ':@' or '@:':
            self.keyboard = True
        else:
            raise SyntaxError('Cannot understand directive ~{}C'
                              .format(self.options_str))
        return True

    def fn(self, arg: str):
        if self.options is None:
            return str(arg)
        if self.read_back:
            return repr(arg)
        if self.spelled_out:
            return CharFn.spell_out(arg)
        if self.keyboard:
            return CharFn.keyboard(arg)
        return arg

    @classmethod
    def spell_out(cls, char: str):
        if char in cls.SPELL_OUT:
            return cls.SPELL_OUT[char]
        return char

    @classmethod
    def keyboard(cls, char: str):
        if char.isupper():
            return 'Shift-{}'.format(CharFn.spell_out(char))
        if len(char) is 2 and char.startswith('^'):
            return 'Control-{}'.format(CharFn.spell_out(char[1]))


class FreshLineFn(StatusFn):
    def __init__(self, pieces=None, options=None):
        super().__init__(pieces, options)
        self.count = 1
        self.init_option()

    def init_option(self):
        if not self.options_str:
            return
        try:
            count = int(self.options_str)
            if count < 0:
                raise ValueError()
        except:
            raise SyntaxError('Cannot understand directive ~{}&'
                              .format(self.options_str))
        else:
            self.count = count

    def fn(self):
        if self.count is 0:
            return ''
        for piece in self.pieces:
            if '\n' in piece:
                return '\n' * self.count
        return '\n' * (self.count-1)

#################
# Below, functions to make a fn
#################

CLASS_ROUTER = {
    'A': AnyFn,
    'W': WriteFn,
    'C': CharFn,
    '&': FreshLineFn
}


def make_fn_obj(directive=None, index=None, options=None):
    """
    make fn-object for the following directives:
        ~A, ~W, ~C, ~&
    """
    fn_class = CLASS_ROUTER.get(directive, NotImplemented)
    if fn_class is NotImplemented:
        raise SyntaxError('Directive \'~{}{}\' not implemented '
                          'or not registered in `CLASS_ROUTER`'
                          .format(options, directive))
    # As fn has not been removed, but not used any more,
    # I'm passing a None here
    if issubclass(fn_class, ArgFn):
        return fn_class(index=index, options=options)
    elif issubclass(fn_class, StatusFn):
        return fn_class(options=options)


def _count_atom(atoms: list, find: type):
    counter = 0
    for atom in atoms:
        if isinstance(atom, find):
            counter += 1
    return counter


def combine_atoms(atoms: list):
    """
    Combine a set of Fn-Objects into a single callable.
    """
    _arg_count = _count_atom(atoms, ArgFn) + _count_atom(atoms, IterFn)
    _kwarg_count = _count_atom(atoms, KwFn)

    def _combine_atoms(*args, **kwargs):
        if len(args) != _arg_count:
            raise ValueError("Need {} of args, got {}"
                             .format(_arg_count, len(args)))
        if len(kwargs) != _kwarg_count:
            raise ValueError("Need {} of kwargs, got {}"
                             .format(_kwarg_count, len(kwargs)))
        pieces = []
        for atom in atoms:
            if isinstance(atom, ArgFn):
                pieces.append(atom(*args))
            elif isinstance(atom, IterFn):
                pieces.append(atom(*args))
            elif isinstance(atom, StatusFn):
                atom.set_pieces(pieces)
                pieces.append(atom())
            elif isinstance(atom, str):
                pieces.append(atom)
            else:
                raise TypeError('Error occurred during combing atoms. '
                                'ArgFn/KwFn objects excepted, got {}.'
                                .format(str(type(atom))))
        return ''.join(pieces)

    return _combine_atoms
