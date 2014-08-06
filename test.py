#encoding=utf-8
from fn import clformat


def main():
    s = clformat(True, '~{~:A、~%~{~A~A~T~{~W,~}~}~%~}', ['一', [1, 2, ['a', 'b']], '二', [1, 2, ['a', 'b']]])
    print(s, type(s))


if __name__ == '__main__':
    main()