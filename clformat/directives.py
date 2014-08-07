#encoding=utf-8
"""
All the functions & classes is implemented here.
"""
from itertools import cycle
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
        self.directive = None

    def __call__(self, *args, **kwargs):
        """
        as the __call__ method of object itself looks like:
            __call__(self, *args, **kwargs)
        and I'm not gotta change it, processing `args` needs extra attention.
        """
        pass

    def init_option(self):
        """
        If needed, this function will be invoke manually in __init__
        to initialize the self.options.
        The return value is ignored.
        """
        return self.options_str

    def parse_prefix(self, only_these=False):
        """
        Read the option_str, and return :, @, :@ flags.
        For C, R, B, D, O, H, etc.
        """
        if self.options_str is ':':
            return True, False, False
        elif self.options_str is '@':
            return False, True, False
        elif self.options_str in {':@', '@:'}:
            return False, False, True
        elif only_these:
            self.make_syntax_error()
        else:
            return False, False, False

    def make_syntax_error(self):
        return SyntaxError('Cannot understand ~{}{}'
                           .format(self.options_str,
                                   self.directive))

    @classmethod
    def parses_ints(cls, *args, empty_as_zero=True):
        def _empty_as_zero(s):
            if s is '':
                return 0
            return int(s)

        functor = int
        if empty_as_zero:
            functor = _empty_as_zero
        return tuple(map(functor, args))

    @classmethod
    def parses_ints_by_index(cls, arr, *args):
        return cls.parses_ints(*(arr[i] for i in args))


class ArgFn(Fn):
    """
    The base class designed to handle the directives
    that only uses positional arguments.
    """

    def __init__(self, index=None, options=None):
        super().__init__(index=index, options=options)

    def fn(self, arg):
        pass

    def __call__(self, *args, **kwargs):
        if self.index is None:
            return self.fn(args[0])
        return self.fn(args[self.index])


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
                raise TypeError('Except Fn or str. {} get.'
                                .format(type(atom)))
        return ''.join(pieces)


class StatusArgFn(ArgFn):
    """
    The base
    """
    pass


class KwFn(Fn):
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
        # '\l': 'Linefeed',
        # '\a': 'Rubout'
    }

    def __init__(self, index=None, options=None):
        super().__init__(index=index, options=options)
        self.directive = 'C'
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
            raise self.make_syntax_error()
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


class RadixFn(ArgFn):
    DIGITS_36 = string.digits + string.ascii_uppercase

    def __init__(self, index=None, options=None):
        super().__init__(index, options)
        self.directive = 'R'
        self.eng = False
        self.ord_eng = False
        self.roman = False
        self.old_roman = False
        self.radix = 0
        self.mincol = 0
        self.interval = 0
        self.pad_char = ''
        self.comma_char = ''
        self.init_option()

    def init_option(self):
        # When meet ~R
        if not self.options_str:
            self.eng = True
            return
        # when meet ~:R ~@R ~@:R ~:@R
        else:
            has_colon, has_at, has_colon_at = self.parse_prefix()
            if not (has_colon or has_at or has_colon_at):
                self.eng = True
            if has_colon:
                self.ord_eng = True
            if has_at:
                self.roman = True
            if has_colon_at:
                self.old_roman = True
        if self.options_str.endswith(':'):
            self.options_str = self.options_str[:-1]
        pieces = self.options_str.split(',')
        if len(pieces) is not 5:
            raise self.make_syntax_error()
        self.radix, self.mincol, self.interval = \
            Fn.parses_ints_by_index(pieces, 0, 1, 4)
        self.pad_char, self.comma_char = \
            RadixFn.parse_quoted_chars(*pieces[2:4])

    def fn(self, value):
        # TODO handle eng & roman
        r_digits = RadixFn.radix_convert_digits(value, self.radix)
        # here, insert the comma char if needed
        # list.insert will insert an element before the index
        # hence the indexes should be:
        # i = k, 2k+1, 3k+2 ... nk+n-1, i <= L+L//k
        # where k is self.interval and L is then length of digits
        if self.interval:
            l = len(r_digits)
            k = self.interval
            index = [n * k + n - 1 for n in range(1, k) if
                     n * k + n - 1 <= l + l // k]
            for i in index:
                r_digits.insert(i, self.comma_char)
        # now check the new length and insert pac char if needed
        length = len(r_digits)
        if length < self.mincol:
            r_digits.append(self.pad_char * (self.mincol - length))
        r_digits.reverse()
        return ''.join(r_digits)

    @classmethod
    def radix_convert_digits(cls, value: int, radix=10):
        if radix is 10:
            return str(value)
        if radix is 2:
            return bin(value)[2:]
        if radix is 8:
            return oct(value)[2:]
        if radix is 16:
            return hex(value)[2:].upper()
        if 2 <= radix <= 36:
            value_abs = abs(value)
            digits = []
            while value_abs > 0:
                value_abs, remain = divmod(value_abs, radix)
                digits.append(RadixFn.DIGITS_36[remain])
            return digits
        else:
            raise ValueError('Cannot convert integer into base {}'
                             .format(radix))

    @classmethod
    def radix_convert(cls, value: int, radix=10):
        return ''.join(RadixFn.radix_convert_digits(value, radix).reverse())


    @classmethod
    def parse_quoted_chars(cls, *chars: list):
        retval = []
        for char in chars:
            if len(char) is 2 and char.startswith('\''):
                retval.append(char[1])
            elif len(char) is 0:
                retval.append(char)
            else:
                raise ValueError('\'{}\' is not a valid quoted character.'
                                 .format(char))
        return retval


class FreshLineFn(StatusFn):
    def __init__(self, pieces=None, options=None):
        super().__init__(pieces, options)
        self.directive = '&'
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
            raise self.make_syntax_error()
        else:
            self.count = count

    def fn(self):
        if self.count is 0:
            return ''
        for piece in self.pieces:
            if '\n' in piece:
                return '\n' * self.count
        return '\n' * (self.count - 1)

#################
# Below, functions to make a fn
#################

CLASS_ROUTER = {
    # Basic directives
    'C': CharFn,
    '&': FreshLineFn,
    # Radix directives
    'R': RadixFn
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
                                'Fn objects excepted, got {}.'
                                .format(str(type(atom))))
        return ''.join(pieces)

    return _combine_atoms
