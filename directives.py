#encoding=utf-8
"""
All the functions & classes is implemented here.
"""
from itertools import cycle


#############
# Fn class that handles the directives
# which will be applied on each argument.
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
    # TODO try make this compatible with the origin {key} notations of Python
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

REGISTERED_FN_CLASS = AnyFn, WriteFn, IterFn

#################
# Below, functions to make a fn
#################

CLASS_ROUTER = {
    'A': AnyFn,
    'W': WriteFn,
}

FUNCTION_ROUTER = {
    'A': AnyFn,
    'W': WriteFn,
}


def make_fn_obj(directive, index, options):
    """
    make fn-object for the following directives:
        ~A, ~W, ~C, ~$, ~D,
    """
    fn_class = CLASS_ROUTER.get(directive, default=NotImplemented)
    fn = make_fn(directive, options)
    if fn_class is NotImplemented:
        raise SyntaxError('Directive \'~{}{}\' not implemented '
                          'or not registered in `CLASS_ROUTER`'
                          .format(options, directive))
    return fn_class(fn=fn, index=index, options=options)


def make_fn(directive, options):
    """
    Make the callable `fn` to initialize the Fn-Class objects.
    """
    func = FUNCTION_ROUTER.get(directive, default=NotImplemented)
    if func is NotImplemented:
        raise SyntaxError('Directive \'~{}{}\' not implemented '
                          'or not registered in `FUNCTION_ROUTER`'
                          .format(options, directive))
    # TODO handle any possible exception raised in func
    return func(options)


def _count_atom(atoms: list, find: type):
    counter = 0
    for atom in atoms:
        if isinstance(atom, find):
            counter += 1
    return counter


def _atom_caller(arg, kwargs):
    """
    Helper to call the Fn-Objects' __call__ methods.
    """
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


def combine_atoms(atoms: list):
    """
    Combine a set of Fn-Objects into a single callable.
    """
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
