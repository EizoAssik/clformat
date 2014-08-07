#encoding=utf-8
"""
This module implements functions that used in Radix directives.
"""
from .units import *

HUNDREDTH = 'hundredth'
HUNDRED = 'hundred'


def _int_english_3_digits(value, ordinal=False):
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
        if ordinal:
            words.append(CL_DIGITS_TH[base])
        else:
            words.append(CL_DIGITS[base])
    elif 10 <= remains <= 19:
        if ordinal:
            words.append(CL_TEENS_TH[remains])
        else:
            words.append(CL_TEENS[remains])
    # remains >= 20
    else:
        if tens and base:
            if ordinal:
                words.append(CL_TENS[tens] + '-' + CL_DIGITS_TH[base])
            else:
                words.append(CL_TENS[tens] + '-' + CL_DIGITS[base])
        elif not tens and base:
            if ordinal:
                words.append(CL_DIGITS_TH[base])
            else:
                words.append(CL_DIGITS[base])
        else:
            if ordinal:
                words.append(CL_TENS_TH[tens])
            else:
                words.append(CL_TENS[tens])
    return ' '.join(words)


def int_english(value, ordinal=False):
    pieces = []
    digit_count = 0
    combine_last = ordinal
    while value:
        value, digits = divmod(value, 1000)
        if combine_last and digit_count is 0 and digits >= 100:
            combine_last = False
        current = _int_english_3_digits(digits, ordinal=ordinal)
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
    if combine_last:
        second = pieces.pop(0)
        first = pieces.pop(0)
        pieces.insert(0, first + ' ' + second)
    pieces.reverse()
    return ', '.join(pieces)



