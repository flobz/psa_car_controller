import sys

if sys.version_info >= (3, 8):
    from importlib import metadata
else:
    import importlib_metadata as metadata
try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    __version__ = "unknown"

del metadata, sys
