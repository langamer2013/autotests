import paramiko
import time
import pytest
import random

ports = random.randrange(100, 1000)
print(ports)
some_list = [1, 5, 6, 7]


def test(lst):
    a, b, c, d = lst
    print(a)
    print(b)
    print(c)
    print(d)


test(some_list)
