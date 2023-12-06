
_MAJOR, _MINOR, _PATCH, _SUFFIX = ("2", "4", "0", "")

# _PATCH: On main and in a nightly release the patch should be one ahead of the last released build.
# _SUFFIX: This is mainly for nightly builds which have the suffix ".dev$DATE". See
# https://semver.org/#is-v123-a-semantic-version for the semantics.

VERSION_SHORT = f"{_MAJOR}.{_MINOR}"
VERSION = f"{_MAJOR}.{_MINOR}.{_PATCH}{_SUFFIX}"
