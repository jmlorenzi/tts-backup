#!/usr/bin/python3

import json
import re
import os


IMGPATH = os.path.join("Mods", "Images")
OBJPATH = os.path.join("Mods", "Models")

GAMEDATA_DEFAULT = os.path.expanduser(
    "~/Documents/My Games/Tabletop Simulator"
)


def seekURL(dic, trail=[]):
    """Recursively search through the save game structure and return URLs
    and the paths to them.

    """

    for k, v in dic.items():

        newtrail = trail + [k]

        if isinstance(v, dict):
            yield from seekURL(v, newtrail)

        elif isinstance(v, list):
            for elem in v:
                if not isinstance(elem, dict):
                    continue
                yield from seekURL(elem, newtrail)

        elif k.endswith("URL"):
            # Some URL keys may be left empty.
            if not v:
                continue

            # Deck art URLs can contain metadata in curly braces
            # (yikes).
            v = re.sub(r"{.*}", "", v)

            yield (newtrail, v)


# We need checks for whether a URL points to a mesh or an image, so we
# can do the right thing for each.

def is_obj(path, url):
    # TODO: None of my mods have NormalURL set (normal maps?). I’m
    # assuming these are image files.
    obj_keys = ("MeshURL", "ColliderURL")
    return path[-1] in obj_keys


def is_image(path, url):
    # This assumes that we only have mesh and image URLs.
    return not is_obj(path, url)


def recodeURL(url):
    """Recode the given URL in the way TTS does, which yields the
    file-system path to the cached file."""

    return re.sub(r"[\W_]", "", url)


def get_fs_path(path, url):
    """Return a file-system path to the object in the cache."""

    recoded_name = recodeURL(url)

    if is_obj(path, url):
        filename = recoded_name + ".obj"
        return os.path.join(OBJPATH, filename)

    elif is_image(path, url):
        # Evenn PNGs are stored with .jpg suffix by TTS.
        filename = recoded_name + ".jpg"
        return os.path.join(IMGPATH, filename)

    else:
        raise ValueError("Do not know how to generate path for URL %s at %s." %
                         (url, path))


def urls_from_save(filename):

    with open(filename, 'r', encoding='utf-8') as infile:
        save = json.load(infile)
    return seekURL(save)
