# -*- coding: utf-8 -*-
"""One way of turning a title into a card filename.

The cards live in one flat folder, so anything keyed by title rather than by
code needs flattening first. fetch_cards.py writes the files and extras.py
looks them up again, so they have to agree -- hence one function, imported by
both, rather than the same regex written twice.
"""
import re


def slug(title):
    s = re.sub(r"[^A-Za-z0-9]+", "-", title).strip("-").lower()
    return s or "untitled"
