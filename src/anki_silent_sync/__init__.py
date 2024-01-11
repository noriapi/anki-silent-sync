# SPDX-FileCopyrightText: 2024-present noriapi <70106808+noriapi@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT


import aqt.main
from aqt import mw
from aqt.qt import QAction, qconnect

from .sync import on_sync_button_clicked_silent


def register(mw: aqt.main.AnkiQt) -> None:
    action = QAction("Sync Silently", mw)

    def do_sync():
        on_sync_button_clicked_silent(mw)

    qconnect(action.triggered, do_sync)
    mw.form.menuTools.addAction(action)


def main() -> None:
    assert mw is not None
    register(mw)


main()
