# SPDX-FileCopyrightText: 2024-present noriapi <70106808+noriapi@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT

from typing import Callable

import aqt.main
from anki.errors import Interrupted, SyncError, SyncErrorKind
from anki.sync import SyncOutput
from aqt import gui_hooks
from aqt.operations import QueryOp
from aqt.sync import full_sync


def handle_sync_error(mw: aqt.main.AnkiQt, err: Exception) -> None:
    if isinstance(err, SyncError):
        if err.kind is SyncErrorKind.AUTH:
            mw.pm.clear_sync_auth()
    elif isinstance(err, Interrupted):
        # no message to show
        return
    # showWarning(str(err))


# port of aqt.sync.sync_collection
def sync_collection_silent(
    mw: aqt.main.AnkiQt, on_done: Callable[[], None], prompt: bool = False
) -> None:
    auth = mw.pm.sync_auth()
    if not auth:
        raise Exception("expected auth")

    def on_success(out: SyncOutput) -> None:
        mw.pm.set_host_number(out.host_number)
        if out.new_endpoint:
            mw.pm.set_current_sync_url(out.new_endpoint)
        if out.required == out.NO_CHANGES:
            # tooltip(parent=mw, msg=tr.sync_collection_complete())
            # all done; track media progress
            # mw.media_syncer.start_monitoring()
            return on_done()
        else:
            if prompt:
                return full_sync(mw, out, on_done)
            else:
                return on_done()

    def on_failure(err: Exception) -> None:
        handle_sync_error(mw, err)
        return on_done()

    QueryOp(
        parent=mw,
        op=lambda col: col.sync_collection(auth, mw.pm.media_syncing_enabled()),
        success=on_success,
    ).failure(on_failure).run_in_background()


# port of aqt.main.AnkiQt._sync_collection_and_media
def _sync_collection_and_media_silent(
    mw: aqt.main.AnkiQt,
    after_sync: Callable[[], None],
    call_gui_hooks: bool = False,
    refresh_ui: bool = False,
    prompt: bool = False,
) -> None:
    "Caller should ensure auth available."

    def on_collection_sync_finished() -> None:
        assert mw.col is not None
        mw.col.models._clear_cache()
        if call_gui_hooks:
            gui_hooks.sync_did_finish()
        if refresh_ui:
            mw.reset()

        after_sync()

    if call_gui_hooks:
        gui_hooks.sync_will_start()
    sync_collection_silent(mw, on_done=on_collection_sync_finished, prompt=prompt)


# port of aqt.main.AnkiQt.on_sync_button_clicked
def on_sync_button_clicked_silent(
    mw: aqt.main.AnkiQt,
    call_gui_hooks: bool = False,
    refresh_ui: bool = False,
    prompt: bool = False,
) -> None:
    if mw.media_syncer.is_syncing():
        pass
        # mw.media_syncer.show_sync_log()
    else:
        auth = mw.pm.sync_auth()
        if not auth:
            if prompt:
                # do normal operation
                mw.on_sync_button_clicked()
        else:
            _sync_collection_and_media_silent(
                mw,
                mw._refresh_after_sync if refresh_ui else lambda: None,
                call_gui_hooks=call_gui_hooks,
                refresh_ui=refresh_ui,
                prompt=prompt,
            )
