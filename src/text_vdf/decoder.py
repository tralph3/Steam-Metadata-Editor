import re

class TextVdfDecodeError(Exception):
    pass


class TextVdfDecoder:
    def __init__(self, contents: str):
        self.contents = contents

    def decode(self) -> dict:
        self.sanitize_input()

    def sanitize_input(self):
        self.contents = re.sub(r'^\t+', '', self.contents, flags=re.MULTILINE)
        self.contents = self.contents.replace("\n", "")

    def read_string(self) -> str:
        pass
