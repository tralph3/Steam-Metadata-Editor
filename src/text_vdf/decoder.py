import re


REGEX_TAB = re.compile(r'^\t+', flags=re.MULTILINE)
REGEX_PAIR = re.compile(r'"(.*?)"\t\t"(.*?)"')
REGEX_DICTIONARY = re.compile(r'"([^"]+?)"{')


class TextVdfDecodeError(Exception):
    pass


class TextVdfDecoder:
    def __init__(self, contents: str):
        self.contents = contents
        self.pointer = 0

    def decode(self) -> dict:
        self._sanitize_input()
        return self._parse_contents()

    def _sanitize_input(self):
        self.contents = REGEX_TAB.sub('', self.contents)
        self.contents = self.contents.replace("\n", "")
        self.contents += "\n"

    def _parse_contents(self) -> dict:
        results = {}
        while self.contents[self.pointer] not in "}\n":
            dict_match = REGEX_DICTIONARY.search(self.contents, pos=self.pointer)
            if dict_match and dict_match.start() == self.pointer:
                key = dict_match.group(1)
                self.pointer = dict_match.end()
                results[key] = self._parse_contents()
            else:
                key, val = self._parse_pair()
                results[key] = val
        self.pointer += 1
        return results

    def _parse_pair(self) -> (str, str):
        match = REGEX_PAIR.search(self.contents, pos=self.pointer)
        if not match or len(match.groups()) != 2:
            raise TextVdfDecodeError("Unexpected key/value format")
        self.pointer = match.end()
        return (match.group(1), match.group(2))
