#!/usr/bin/env python3

import textwrap


def code_block(text: str) -> str:
    """Helper function to dedent and strip code blocks for tests."""
    return textwrap.dedent(text).strip()