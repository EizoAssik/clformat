#encoding=utf-8
"""
This module implements functions that used in Radix directives.
"""
from .units import *
from math import log10, floor

HUNDREDTH = 'hundredth'
HUNDRED = 'hundred'


def _count_digits(digits):
    if isinstance(digits, int):
        return floor(log10(digits)) if digits > 0 else 0
    elif isinstance(digits, str):
        return len(digits)
    else:
        raise TypeError('\'{}\' as {} not countable.'
                        .format(digits, type(digits)))


def _spell_3_digits(value, ordinal=False):
    """
    Format 3-digits values into a string.
    """
    if value is 0:
        return ''
    words = []
    hundreds, remains = divmod(value, 100)
    tens, base = divmod(remains, 10)
    if hundreds:
        words.append(CL_DIGITS[hundreds])
        words.append(HUNDRED)
    if remains is 0:
        return ' '.join(words)
    if hundreds and remains and not ordinal:
        words.append('and')
    if 0 < remains <= 9:
        words.append(CL_DIGITS[base])
    elif 10 <= remains <= 19:
        words.append(CL_TEENS[remains])
    else:
        if tens and base:
            words.append(CL_TENS[tens] + '-' + CL_DIGITS[base])
        elif not tens and base:
            words.append(CL_DIGITS[base])
        else:
            words.append(CL_TENS[tens])
    return ' '.join(words)


def spell_int(value, ordinal=False):
    pieces = []
    digit_count = 0
    while value:
        value, digits = divmod(value, 1000)
        current = _spell_3_digits(digits, ordinal=ordinal)
        # when the lowest 3-digits is made ordinal
        # then no more ordinal-digits needed
        if current and ordinal:
            ordinal = False
        if digit_count:
            pieces.append('{} {}'
                          .format(current,
                                  CL_UNITS[digit_count]))
        else:
            pieces.append(current)
        digit_count += 3
    pieces.reverse()
    return ', '.join(pieces)
