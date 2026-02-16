import requests
from pprint import pprint
url = "https://google.com"
page = requests.request(method='GET', url=url)
# page.content
pprint(dir(page))


class Example:
    def __init__(self, test):
        self.test = test

    def say(self):
        print(self.test)
