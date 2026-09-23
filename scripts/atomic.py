# Copyright (c) 2026 Jason D. Gower
# SPDX-License-Identifier: MIT
"""Single atomic file writer for scripts that emit committed artifacts."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path


def write_atomic(path: Path, text: str) -> None:
    """Write via a temporary file in the same directory, then replace.

    A crash must never leave a half-written destination. Readers see the old
    file or the new file, never a partial write (os.replace is atomic on POSIX;
    same pattern build already used).
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
    except Exception:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise
    os.replace(temporary, path)
