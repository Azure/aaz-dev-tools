"""
MonkeyType configuration for aaz-dev-tools.

Usage — trace, then apply:
    PYTHONPATH=src/aaz_dev:src python -m monkeytype run -m pytest \
        src/aaz_dev/command/tests/configuration_tests/ \
        src/aaz_dev/command/tests/editor_tests/test_serialize_shorthand.py \
        --ignore=src/aaz_dev/command/tests/configuration_tests/test_xml.py \
        -q

    python -m monkeytype list-modules
    python -m monkeytype apply <module>

Notes:
- The code_filter restricts tracing to src/aaz_dev/ only, keeping Flask/schematics
  stdlib internals out of the trace database.
- Module names in the DB use the unqualified form (e.g. "utils.case") because the
  codebase adds src/aaz_dev/ to sys.path. Apply with those unqualified names.
"""

import os
from monkeytype.config import DefaultConfig
from monkeytype.typing import NoOpRewriter


_REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
_SOURCE_ROOT = os.path.join(_REPO_ROOT, "src", "aaz_dev")


class AazDevConfig(DefaultConfig):
    def code_filter(self):  # type: ignore[override]
        """Only trace code that lives inside src/aaz_dev/."""
        source_root = _SOURCE_ROOT

        def _filter(code):  # type: ignore[no-untyped-def]
            filename = code.co_filename or ""
            return filename.startswith(source_root)

        return _filter


CONFIG = AazDevConfig()
