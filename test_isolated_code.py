import paramiko
import time
import pytest
import random

ports = random.randrange(100, 1000)
print(ports)
list = [1, 5, 6, 7]

def test(list):
    a, b, c, d = list
    print(a)
    print(b)
    print(c)
    print(d)

test(list)