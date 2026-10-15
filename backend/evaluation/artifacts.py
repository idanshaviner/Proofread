"""Local paired evaluation output with exclusive creation and checked rollback."""
from contextlib import ExitStack
import json
import os
from pathlib import Path
from typing import Any


def write_review_pair(review_path: str | Path, review: Any,
                      key_path: str | Path, key: Any) -> None:
    """Write a review and its separate answer key without overwriting files.

    Both documents are serialized before either destination is created. Each
    destination is created exclusively, and both are open before writing starts.
    Ordinary creation/write/flush/close failures remove files this invocation
    created, provided their device/inode identities still match. Observed user
    replacements are preserved; rollback failures are noted on the original error.

    This is not a crash-atomic transaction across two paths. Abrupt process or
    machine failure may leave partial artifacts. Identity-check/unlink is also not
    atomic against a concurrent rename between those operations; this helper does
    not support adversarial concurrent mutation of the destination directories.
    """
    paths = (Path(review_path), Path(key_path))
    if paths[0].resolve() == paths[1].resolve():
        raise ValueError("Review and key must use separate paths")
    payloads = tuple(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
                     for value in (review, key))
    created = []
    try:
        with ExitStack() as stack:
            handles = []
            for path in paths:
                descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
                try:
                    identity = os.fstat(descriptor)
                    created.append((path, identity.st_dev, identity.st_ino))
                    handle = os.fdopen(descriptor, "w", encoding="utf-8")
                except BaseException:
                    os.close(descriptor)
                    raise
                handles.append(stack.enter_context(handle))
            for handle, payload in zip(handles, payloads):
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
    except BaseException as exc:
        for path, device, inode in reversed(created):
            try:
                current = path.lstat()
                if (current.st_dev, current.st_ino) == (device, inode):
                    path.unlink()
            except FileNotFoundError:
                pass
            except OSError:
                exc.add_note(f"Rollback could not remove invocation-owned artifact: {path}")
        raise
