class TextVdfEncoder:
    pass


def dict_to_vdf(vdf_dict: dict, indent=0) -> bytearray:
    result = bytearray()
    tabs = b"\t" * indent
    for key in vdf_dict.keys():
        if isinstance(vdf_dict[key], dict):
            indent += 1
            result += (tabs
                + b'"'
                + key.replace("\\", "\\\\").encode()
                + b'"\n'
                + tabs
                + b"{\n"
                + dict_to_vdf(vdf_dict[key], indent)
                + tabs
                + b"}\n")
            indent -= 1
        else:
            result += (tabs
                + b'"'
                + key.replace("\\", "\\\\").encode()
                + b'"'
                + b"\t\t"
                + b'"'
                + str(vdf_dict[key]).replace("\\", "\\\\").encode()
                + b'"\n')
    return result
