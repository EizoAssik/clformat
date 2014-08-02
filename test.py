#encoding=utf-8
from fn import clformat


def main():
    s = clformat(True, '~{~a -> ~{~A,~}~%~}', [1, [1, 2], 2, [2, 3], 3, [3, 4]])
    # s = clformat(True, "Hello World ~a ~~ ~{~A~}", 1, [1, 2])
    print(s, type(s))


if __name__ == '__main__':
    main()