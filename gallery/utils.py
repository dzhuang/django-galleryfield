
def convert_dict_to_plain_text(d, indent=4):
    result = []
    for k, v in d.items():
        if v is not None:
            result.append(" " * indent + "%s: %s," % (k, str(v)))
    return "\n".join(result)
