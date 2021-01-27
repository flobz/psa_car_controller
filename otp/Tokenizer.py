from locale import atoi


class Tokenizer(object):
    def __init__(self, str, delimiter="&&"):
        self.s:str = str
        self.delimiter = delimiter
        self.currentIndex = 0

    def nextToken(self):
        if self.currentIndex >= len(self.s):
            return ""
        indexOf = self.currentIndex+self.s[self.currentIndex:].index(self.delimiter)
        if indexOf == -1:
            substring = self.s[self.currentIndex:]
            self.currentIndex = self.s.length()
            return substring

        substring2 = self.s[self.currentIndex:indexOf]
        self.currentIndex = indexOf + len(self.delimiter)
        #print(f"{substring2} index:{self.currentIndex}")
        return substring2

    def nextTokenI(self):
        token = self.nextToken()
        if token == "":
            return 0
        else:
            return int(token, 16)

    def hasMoreTokens(self):
        return self.currentIndex < len(self.s)

# a="0.2.11&&&&&&0&&0&&0&&9f13ba238fbabba08e85d93638e98ef5e48682a9d3e5bc325c3dd6fac8199a6ce09e9b4f373aa6a75a905c3d690f6e3335d1e8e5b748ecec3020a794149033f6ada6896db6d73b8d43b8365bbe15b9ac66f49d4e684a3628f1e9f3deda0c4e24aba771946e6085b92c5ad312477152acf8db01e6aea4b409d5ac1a05c2fd4e95&&0&&&&&&&&&&&&0&&0&&0&&0&&0&&0&&0&&&&&&&&0&&0&&0&&0&&0&&2.0.0&&http://m.inwebo.com/&&"
# t=Tokenizer(a)
# self = t
# t.nextToken()
# t.nextToken()
# t.currentIndex
# t.nextTokenI()
# atoi("")