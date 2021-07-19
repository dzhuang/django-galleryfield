import re

def convert_dict_to_plain_text(d, indent=4):
    result = []
    for k, v in d.items():
        if v is not None:
            result.append(" " * indent + "%s: %s," % (k, str(v)))
    return "\n".join(result)


def get_thumbnail_from_file_path(file_path, **kwargs):

    def thumbnail_format(path):
        match = re.search(r'\.\w+$', path)
        if match:
            ext = match.group(0)
            if ext.lower() in ['.gif', '.png']:
                return 'PNG'
        return 'JPEG'

    preview_size = kwargs.pop("preview_size", 64)

    generate_kwargs = {
        "geometry_string": "%sx%s" % (preview_size, preview_size),
        "upscale": kwargs.pop("upscale", False),
        "format": kwargs.pop("format", thumbnail_format(file_path))
    }
    from sorl.thumbnail import get_thumbnail
    return get_thumbnail(
        file_path, **generate_kwargs)
