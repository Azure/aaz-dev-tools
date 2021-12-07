# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

import html
import inflect

from lxml.builder import ElementMaker
from lxml.etree import tostring
from schematics import Model


class XMLModel(Model):
    @property
    def xml_root(self):
        return type(self).__name__

    def to_xml(self):
        primitive = self.to_primitive()
        root = self._build_xml(primitive)
        return html.unescape(
            tostring(root, xml_declaration=True, pretty_print=True, encoding="utf-8").decode()
        )

    def _build_xml(self, primitive, parent=None):
        linker = ElementMaker()
        if parent is None:
            parent = getattr(linker, self.xml_root)()
        # normalize element name
        if curr_tag := inflect.engine().singular_noun(parent.tag):
            parent.tag = curr_tag

        for key, val in primitive.items():
            self._primitive_to_xml(key, val, parent)
        return parent

    def _primitive_to_xml(self, key, value, parent):
        linker = ElementMaker()
        if isinstance(value, dict):
            _parent = getattr(linker, key)()
            parent.append(self._build_xml(value, _parent))
        elif isinstance(value, list):
            for val in value:
                self._primitive_to_xml(key, val, parent)
        else:
            # store metadata as attributes
            if prev := parent.get(key):
                curr = " ".join(sorted(f"{prev} {value}".split(), reverse=True))
                parent.set(key, curr)
            else:
                parent.set(key, str(value))
