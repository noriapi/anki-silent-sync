# SPDX-FileCopyrightText: 2024-present noriapi <70106808+noriapi@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT

from typing import Callable

import aqt.main
from anki.errors import Interrupted, SyncError, SyncErrorKind
from aqt import mw
from aqt.qt import QAction, qconnect
from aqt.sync import full_sync
from aqt.utils import showInfo


# We're going to add a menu item below. First we want to create a function to
# be called when the menu item is activated.
def handle_sync_error(mw: aqt.main.AnkiQt, err: Exception) -> None:
    if isinstance(err, SyncError):
        if err.kind is SyncErrorKind.AUTH:
            mw.pm.clear_sync_auth()
    elif isinstance(err, Interrupted):
        # no message to show
        return
    # showWarning(str(err))


def sync_collection_silent(mw: aqt.main.AnkiQt, on_done: Callable[[], None]) -> None:
    assert mw is not None

    auth = mw.pm.sync_auth()
    if not auth:
        raise Exception("expected auth")

    assert mw.col is not None

    try:
        out = mw.col.sync_collection(auth, mw.pm.media_syncing_enabled())
    except Exception as err:
        handle_sync_error(mw, err)
        return on_done()

    mw.pm.set_host_number(out.host_number)
    if out.new_endpoint:
        mw.pm.set_current_sync_url(out.new_endpoint)
    if out.required == out.NO_CHANGES:
        # tooltip(parent=mw, msg=tr.sync_collection_complete())
        # all done; track media progress
        # mw.media_syncer.start_monitoring()
        return on_done()
    else:
        full_sync(mw, out, on_done)


def register() -> None:
    assert mw is not None
    # create a new menu item, "test"
    action = QAction("Sync silent", mw)

    def on_done():
        showInfo("done!")
        pass

    def do_sync():
        assert mw is not None
        sync_collection_silent(mw, on_done)

    # set it to call testFunction when it's clicked
    qconnect(action.triggered, do_sync)
    # and add it to the tools menu
    mw.form.menuTools.addAction(action)


def main() -> None:
    register()


main()
