# pylint: disable=invalid-name
class Tokenizer:
    def __init__(self, tokens, delimiter="&&"):
        self.s: str = tokens
        self.delimiter = delimiter
        self.currentIndex = 0

    def nextToken(self):
        if self.currentIndex >= len(self.s):
            return ""
        index_of = self.currentIndex + self.s[self.currentIndex:].index(self.delimiter)
        if index_of == -1:
            substring = self.s[self.currentIndex:]
            self.currentIndex = len(self.s)
            return substring

        substring2 = self.s[self.currentIndex:index_of]
        self.currentIndex = index_of + len(self.delimiter)
        return substring2

    def nextTokenI(self):
        token = self.nextToken()
        if token == "":
            return 0
        return int(token, 16)

    def hasMoreTokens(self):
        return self.currentIndex < len(self.s)
