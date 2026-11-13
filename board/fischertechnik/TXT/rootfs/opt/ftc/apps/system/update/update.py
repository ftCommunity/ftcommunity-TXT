#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""System Update app for searching, configuring sources, and installing firmware updates."""

import configparser
import html
from html.parser import HTMLParser
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request

from PyQt5 import QtCore
from launcher import LauncherPlugin
from TouchStyle import (
    BusyAnimation,
    DEV,
    QAbstractItemView,
    QApplication,
    QCoreApplication,
    QGraphicsBlurEffect,
    QHBoxLayout,
    QIcon,
    QLabel,
    QLineEdit,
    QListView,
    QListWidget,
    QListWidgetItem,
    QLocale,
    QProgressBar,
    QPushButton,
    QScroller,
    QSize,
    Qt,
    QTextEdit,
    QThread,
    QTimer,
    QTranslator,
    QVBoxLayout,
    QWidget,
    TXT,
    TXPI,
    TouchApplication,
    TouchDialog,
    TouchMessageBox,
    TouchWindow,
    pyqtSignal,
)

try:
    import semantic_version
except ImportError:
    semantic_version = None

APP_DIR = os.path.dirname(os.path.realpath(__file__))
VERSION_FILE = "/etc/fw-ver.txt"
BOOT_BACKUP_MARKER = "/media/sdcard/boot/system-old/rootfs.img"
DEFAULT_SOURCE = "ftCommunity/ftcommunity-TXT"
USER_AGENT = "ftcommunity-TXT-updater/1.2"
CONFIG_FILE = os.path.expanduser("~/.system-update.ini")
CACHE_DIR = os.path.expanduser("~/.system-update-cache")
SYSTEM_UPDATE_BIN = "/sbin/system-update"
CHUNK_SIZE = 65536


def read_current_version():
    """Read installed firmware version from /etc/fw-ver.txt."""
    try:
        with open(VERSION_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return ""


def load_saved_source():
    """Load configured update source from ~/.system-update.ini."""
    cfg = configparser.RawConfigParser()
    try:
        if os.path.isfile(CONFIG_FILE):
            cfg.read(CONFIG_FILE, encoding="utf-8")
            val = cfg.get("update", "source", fallback="").strip()
            if val:
                return val
    except Exception:
        pass
    return DEFAULT_SOURCE


def save_source(source):
    """Persist update source in ~/.system-update.ini."""
    cfg = configparser.RawConfigParser()
    cfg.add_section("update")
    cfg.set("update", "source", source.strip() or DEFAULT_SOURCE)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        cfg.write(f)


def normalize_source(raw_source):
    """Classify a user source string as ('github', owner_repo) or ('url', url)."""
    src = (raw_source or "").strip()
    if not src:
        return ("github", DEFAULT_SOURCE)

    github_match = re.match(
        r"^https?://(?:www\.)?github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+?)(?:\.git|/releases.*|/)?$",
        src,
        re.IGNORECASE,
    )
    if github_match:
        return ("github", github_match.group(1))

    if re.match(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", src):
        return ("github", src)

    if not re.match(r"^https?://", src, re.IGNORECASE):
        src = "http://" + src
    return ("url", src)


def _version_tuple(ver_str):
    """Fallback numeric version key for arbitrary version strings."""
    cleaned = (ver_str or "").strip().lstrip("vV")
    core, *rest = re.split(r"[-~+]", cleaned, maxsplit=1)
    core_nums = [int(x) for x in re.findall(r"\d+", core)]
    if not core_nums:
        return None
    while len(core_nums) < 4:
        core_nums.append(0)
    is_release = 0 if rest else 1
    pre_nums = tuple(int(x) for x in re.findall(r"\d+", rest[0])) if rest else ()
    return tuple(core_nums[:4] + [is_release]) + pre_nums


def compare_versions(candidate, current):
    """Compare candidate vs current version: 1 newer, 0 same, -1 older, None unknown."""
    cand_s = (candidate or "").strip().lstrip("vV")
    curr_s = (current or "").strip().lstrip("vV")
    if not cand_s or not curr_s:
        return None
    if semantic_version is not None:
        try:
            v_cand = semantic_version.Version.coerce(cand_s)
            v_curr = semantic_version.Version.coerce(curr_s)
            if v_cand > v_curr:
                return 1
            if v_cand == v_curr:
                return 0
            return -1
        except ValueError:
            pass
    t_cand = _version_tuple(cand_s)
    t_curr = _version_tuple(curr_s)
    if t_cand is None or t_curr is None:
        return 0 if cand_s == curr_s else None
    if t_cand > t_curr:
        return 1
    if t_cand == t_curr:
        return 0
    return -1


def extract_version_from_filename(filename):
    """Extract firmware version label from a ZIP filename."""
    base = os.path.basename(filename)
    m = re.match(r"^ftcommunity-txt-(.+)\.zip$", base, re.IGNORECASE)
    if m:
        return m.group(1)
    if base.lower().endswith(".zip"):
        return base[:-4]
    return base


def format_size_mb(size_bytes):
    """Format byte count cleanly in MB for compact touch UI."""
    if not size_bytes or size_bytes <= 0:
        return ""
    return f"{size_bytes / (1024 * 1024):.1f} MB"


class _ZipLinkParser(HTMLParser):
    """Collect href links ending with .zip from HTML directory listings."""

    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "a":
            return
        for key, val in attrs:
            if key.lower() == "href" and val:
                path_part = urllib.parse.urlsplit(val).path
                if path_part.lower().endswith(".zip"):
                    self.links.append(val)


def _http_get(url, accept=None, timeout=15, max_bytes=2 * 1024 * 1024):
    """Perform an HTTP GET with bounded read size."""
    headers = {"User-Agent": USER_AGENT}
    if accept:
        headers["Accept"] = accept
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read(max_bytes + 1)
        if len(data) > max_bytes:
            raise ValueError("Response too large")
        return data, resp.headers


def _head_size(url, timeout=6):
    """Best-effort Content-Length lookup via HTTP HEAD."""
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return int(resp.headers.get("Content-Length") or 0)
    except Exception:
        return 0


def _pick_zip_asset(release_obj):
    """Select the firmware ZIP asset from a GitHub-style release JSON object."""
    assets = release_obj.get("assets") or []
    for asset in assets:
        name = asset.get("name", "")
        ctype = asset.get("content_type", "")
        if name.lower().endswith(".zip") or ctype in ("application/zip", "application/x-zip-compressed"):
            url = asset.get("browser_download_url") or asset.get("url") or ""
            if url:
                return name, url, int(asset.get("size") or 0)
    direct_url = release_obj.get("url") or ""
    if isinstance(direct_url, str) and direct_url.lower().endswith(".zip"):
        return os.path.basename(direct_url), direct_url, int(release_obj.get("size") or 0)
    return None


def _build_release_entry(tag, version, url, size, published, notes, prerelease, current_ver, filename=""):
    """Construct normalized release metadata dictionary."""
    clean_ver = (version or tag or "").strip().lstrip("vV")
    return {
        "tag": tag or clean_ver,
        "version": clean_ver,
        "url": url,
        "size": int(size or 0),
        "published": (published or "")[:10],
        "notes": (notes or "").strip(),
        "prerelease": bool(prerelease),
        "filename": filename or os.path.basename(urllib.parse.urlsplit(url).path),
        "cmp": compare_versions(clean_ver, current_ver),
    }


def _parse_json_releases(payload, current_ver):
    """Parse GitHub release list or custom release JSON structures."""
    if isinstance(payload, dict):
        items = payload.get("releases")
        if isinstance(items, list):
            return _parse_json_releases(items, current_ver)
        items = [payload]
    elif isinstance(payload, list):
        items = payload
    else:
        return []

    releases = []
    for item in items:
        if not isinstance(item, dict) or item.get("draft"):
            continue
        asset = _pick_zip_asset(item)
        if not asset:
            continue
        filename, dl_url, size = asset
        tag = item.get("tag_name") or item.get("version") or item.get("name") or extract_version_from_filename(filename)
        releases.append(
            _build_release_entry(
                tag=str(tag),
                version=str(item.get("version") or tag),
                url=dl_url,
                size=size,
                published=str(item.get("published_at") or item.get("date") or ""),
                notes=str(item.get("body") or item.get("notes") or ""),
                prerelease=item.get("prerelease", False),
                current_ver=current_ver,
                filename=filename,
            )
        )
    return releases


def fetch_releases(raw_source, current_ver):
    """Fetch and parse available firmware releases from a GitHub repo or custom URL."""
    kind, target = normalize_source(raw_source)
    if kind == "github":
        api_url = f"https://api.github.com/repos/{target}/releases?per_page=25"
        raw, _ = _http_get(api_url, accept="application/vnd.github+json")
        data = json.loads(raw.decode("utf-8"))
        return _parse_json_releases(data, current_ver)

    path_lower = urllib.parse.urlsplit(target).path.lower()
    if path_lower.endswith(".zip"):
        ver = extract_version_from_filename(target)
        size = _head_size(target)
        return [
            _build_release_entry(
                tag=ver,
                version=ver,
                url=target,
                size=size,
                published="",
                notes="",
                prerelease=False,
                current_ver=current_ver,
            )
        ]

    raw, headers = _http_get(target)
    ctype = (headers.get("Content-Type") or "").lower()
    text = raw.decode("utf-8", errors="replace")
    if "json" in ctype or text.lstrip().startswith(("[", "{")):
        return _parse_json_releases(json.loads(text), current_ver)

    parser = _ZipLinkParser()
    parser.feed(text)
    seen = set()
    releases = []
    for href in parser.links:
        full_url = urllib.parse.urljoin(target if target.endswith("/") else target + "/", href)
        if full_url in seen:
            continue
        seen.add(full_url)
        ver = extract_version_from_filename(full_url)
        size = _head_size(full_url) if len(seen) <= 10 else 0
        releases.append(
            _build_release_entry(
                tag=ver,
                version=ver,
                url=full_url,
                size=size,
                published="",
                notes="",
                prerelease=False,
                current_ver=current_ver,
            )
        )
    releases.sort(key=lambda r: _version_tuple(r["version"]) or (0, 0, 0, 0, 0), reverse=True)
    return releases


class ReleaseFetchThread(QThread):
    """Background worker fetching release list without blocking UI."""

    finished_ok = pyqtSignal(list)
    finished_err = pyqtSignal(str)

    def __init__(self, source, current_ver):
        super().__init__()
        self.source = source
        self.current_ver = current_ver

    def run(self):
        try:
            releases = fetch_releases(self.source, self.current_ver)
            self.finished_ok.emit(releases)
        except urllib.error.HTTPError as exc:
            if exc.code in (403, 429):
                self.finished_err.emit(f"HTTP {exc.code}: {exc.reason}")
            else:
                self.finished_err.emit(f"HTTP {exc.code}: {exc.reason}")
        except (urllib.error.URLError, OSError, ValueError, json.JSONDecodeError) as exc:
            self.finished_err.emit(str(exc))


class InstallWorker(QThread):
    """Background worker streaming download (if needed) and executing sudo system-update."""

    step_changed = pyqtSignal(str)
    progress_changed = pyqtSignal(int)
    detail_changed = pyqtSignal(str)
    critical_changed = pyqtSignal(bool)
    finished_result = pyqtSignal(bool, bool, str)  # ok, cancelled, message

    def __init__(self, mode, release=None):
        super().__init__()
        self.mode = mode  # "install" or "restore"
        self.release = release
        self.cancel_event = threading.Event()
        self._proc = None

    def request_cancel(self):
        self.cancel_event.set()

    def _cleanup_cache(self):
        shutil.rmtree(CACHE_DIR, ignore_errors=True)

    def _download_to_cache(self, url, expected_size):
        os.makedirs(CACHE_DIR, exist_ok=True)
        cache_root = os.path.dirname(CACHE_DIR) or "/"
        free_bytes = shutil.disk_usage(cache_root).free
        needed_min = (expected_size * 2 + 32 * 1024 * 1024) if expected_size > 0 else (300 * 1024 * 1024)
        if free_bytes < needed_min:
            raise RuntimeError(f"Insufficient disk space ({free_bytes // (1024 * 1024)} MB free)")

        dest_path = os.path.join(CACHE_DIR, "update.zip")
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=30) as resp, open(dest_path, "wb") as out_f:
            total = expected_size if expected_size > 0 else int(resp.headers.get("Content-Length") or 0)
            downloaded = 0
            last_pct = -1
            while True:
                if self.cancel_event.is_set():
                    return None
                buf = resp.read(CHUNK_SIZE)
                if not buf:
                    break
                out_f.write(buf)
                downloaded += len(buf)
                if total > 0:
                    pct = min(100, int(downloaded * 100 / total))
                    if pct != last_pct:
                        last_pct = pct
                        self.progress_changed.emit(pct)
                        self.detail_changed.emit(
                            f"{downloaded / (1024 * 1024):.1f} / {total / (1024 * 1024):.1f} MB"
                        )
                else:
                    self.detail_changed.emit(f"{downloaded / (1024 * 1024):.1f} MB")
            out_f.flush()
            os.fsync(out_f.fileno())

        if expected_size > 0 and downloaded != expected_size:
            raise RuntimeError(f"Download size mismatch ({downloaded} / {expected_size})")
        return dest_path

    def _run_privileged_updater(self, cmd):
        self._proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        for raw_line in self._proc.stdout:
            line = raw_line.strip()
            if line.startswith("STEP:"):
                step = line[5:]
                if step in ("backup", "install", "sync", "restore"):
                    self.critical_changed.emit(True)
                self.step_changed.emit(step)
            elif line.startswith("PROGRESS:"):
                try:
                    self.progress_changed.emit(int(line[9:]))
                except ValueError:
                    pass
            elif line.startswith("DETAIL:"):
                self.detail_changed.emit(line[7:])

        rc = self._proc.wait()
        stderr_txt = self._proc.stderr.read().strip() if self._proc.stderr else ""
        if rc != 0:
            raise RuntimeError(stderr_txt or f"system-update exited with {rc}")

    def run(self):
        try:
            if self.mode == "restore":
                self.critical_changed.emit(True)
                self.step_changed.emit("restore")
                self._run_privileged_updater(["sudo", "-n", SYSTEM_UPDATE_BIN, "--progress", "--restore"])
                self.finished_result.emit(True, False, "")
                return

            self.step_changed.emit("download")
            self.progress_changed.emit(0)
            expected_size = int(self.release.get("size") or 0)
            archive_path = self._download_to_cache(self.release["url"], expected_size)
            if archive_path is None:
                self.finished_result.emit(False, True, "")
                return

            cmd = [
                "sudo",
                "-n",
                SYSTEM_UPDATE_BIN,
                "--progress",
                "--force",
                "--file",
                archive_path,
            ]
            if expected_size > 0:
                cmd.extend(["--size", str(expected_size)])
            cmd.append(self.release.get("version") or "custom")

            self._run_privileged_updater(cmd)
            self.finished_result.emit(True, False, "")
        except Exception as exc:
            self.finished_result.emit(False, False, str(exc))
        finally:
            self.critical_changed.emit(False)
            self._cleanup_cache()


class FullScreenTouchDialog(TouchDialog):
    """TouchDialog subclass supporting fullscreen .show() without exec_() scroll bugs."""

    def show(self):
        if TXT or (TXPI and not DEV):
            QWidget.showFullScreen(self)
        else:
            TouchDialog.show(self)


class SourceDialog(TouchDialog):
    """Dialog to view and edit the update repository or HTTP(S) URL."""

    source_saved = pyqtSignal(str)

    def __init__(self, current_source, parent):
        super().__init__(QCoreApplication.translate("Source", "Source"), parent)
        self.addConfirm()
        self.setCancelButton()

        vbox = QVBoxLayout()
        vbox.setSpacing(6)
        vbox.setContentsMargins(6, 6, 6, 6)

        lbl = QLabel(QCoreApplication.translate("Source", "GitHub repo or URL:"))
        lbl.setObjectName("smallerlabel")
        lbl.setWordWrap(True)
        vbox.addWidget(lbl)

        self.edit = QLineEdit(current_source, self)
        self.edit.setObjectName("smalllabel")
        vbox.addWidget(self.edit)

        hint = QLabel(QCoreApplication.translate("Source", "e.g. ftCommunity/ftcommunity-TXT or http://IP:8000/"))
        hint.setObjectName("tinylabel")
        hint.setWordWrap(True)
        vbox.addWidget(hint)

        vbox.addStretch()

        btn_official = QPushButton(QCoreApplication.translate("Source", "Use official repo"))
        btn_official.setObjectName("smallerlabel")
        btn_official.clicked.connect(lambda: self.edit.setText(DEFAULT_SOURCE))
        vbox.addWidget(btn_official)

        self.centralWidget.setLayout(vbox)

    def close(self):
        super().close()
        if self.sender() and self.sender().objectName() == "confirmbut":
            self.source_saved.emit(self.edit.text().strip() or DEFAULT_SOURCE)


class InstallDialog(TouchDialog):
    """Modal progress dialog during download, verification, backup, and install."""

    reboot_requested = pyqtSignal()

    def __init__(self, mode, release, parent):
        title = (
            QCoreApplication.translate("Install", "Restore backup")
            if mode == "restore"
            else f"{release.get('version') or release.get('tag')}"
        )
        super().__init__(title, parent)
        self.mode = mode
        self.release = release
        self._critical = mode == "restore"
        self._done = False

        vbox = QVBoxLayout()
        vbox.setSpacing(8)
        vbox.setContentsMargins(8, 8, 8, 8)
        vbox.addStretch()

        self.step_label = QLabel(QCoreApplication.translate("Install", "Preparing..."))
        self.step_label.setObjectName("smallerlabel")
        self.step_label.setAlignment(Qt.AlignCenter)
        self.step_label.setWordWrap(True)
        vbox.addWidget(self.step_label)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        vbox.addWidget(self.progress)

        self.detail_label = QLabel("")
        self.detail_label.setObjectName("tinylabel")
        self.detail_label.setAlignment(Qt.AlignCenter)
        self.detail_label.setWordWrap(True)
        vbox.addWidget(self.detail_label)

        vbox.addStretch()

        self.cancel_btn = QPushButton(QCoreApplication.translate("Install", "Cancel"))
        self.cancel_btn.setObjectName("smallerlabel")
        self.cancel_btn.clicked.connect(self.on_cancel)
        if self._critical:
            self.cancel_btn.setEnabled(False)
            self.titlebar.close.setEnabled(False)
        vbox.addWidget(self.cancel_btn)

        self.centralWidget.setLayout(vbox)

        self.worker = InstallWorker(mode, release)
        self.worker.step_changed.connect(self.on_step)
        self.worker.progress_changed.connect(self.progress.setValue)
        self.worker.detail_changed.connect(self.detail_label.setText)
        self.worker.critical_changed.connect(self.on_critical)
        self.worker.finished_result.connect(self.on_finished)
        self.worker.start()

    def _step_text(self, step):
        mapping = {
            "prepare": QCoreApplication.translate("Install", "Preparing..."),
            "download": QCoreApplication.translate("Install", "Downloading..."),
            "verify": QCoreApplication.translate("Install", "Verifying ZIP..."),
            "backup": QCoreApplication.translate("Install", "Backing up system..."),
            "install": QCoreApplication.translate("Install", "Installing update..."),
            "sync": QCoreApplication.translate("Install", "Syncing SD card..."),
            "restore": QCoreApplication.translate("Install", "Restoring backup..."),
            "done": QCoreApplication.translate("Install", "Completed"),
        }
        return mapping.get(step, step)

    def on_step(self, step):
        self.step_label.setText(self._step_text(step))

    def on_critical(self, critical):
        self._critical = critical
        self.cancel_btn.setEnabled(not critical and not self._done)
        self.titlebar.close.setEnabled(not critical)

    def on_cancel(self):
        if self._critical or self._done:
            return
        self.cancel_btn.setEnabled(False)
        self.step_label.setText(QCoreApplication.translate("Install", "Cancelling..."))
        self.worker.request_cancel()

    def closeEvent(self, event):
        if self._critical:
            event.ignore()
            return
        if not self._done and self.worker.isRunning():
            self.worker.request_cancel()
            self.worker.wait(3000)
        super().closeEvent(event)

    def on_finished(self, ok, cancelled, message):
        self._done = True
        self._critical = False
        self.titlebar.close.setEnabled(True)
        self.cancel_btn.setEnabled(False)

        if cancelled:
            self.close()
            return

        if not ok:
            box = TouchMessageBox(QCoreApplication.translate("Error", "Error"), self)
            box.setText(message or QCoreApplication.translate("Install", "Update failed"))
            box.setTextSize(2)
            box.setPosButton(QCoreApplication.translate("Dialog", "Ok"))
            box.exec_()
            self.close()
            return

        box = TouchMessageBox(QCoreApplication.translate("Install", "Success"), self)
        box.setText(QCoreApplication.translate("Install", "Update installed.\nReboot TXT now to activate?"))
        box.setTextSize(2)
        box.setBtnTextSize(2)
        reboot_lbl = QCoreApplication.translate("Install", "Reboot now")
        later_lbl = QCoreApplication.translate("Install", "Later")
        box.setPosButton(reboot_lbl)
        box.setNegButton(later_lbl)
        ok_click, choice = box.exec_()
        self.close()
        if ok_click and choice == reboot_lbl:
            self.reboot_requested.emit()


class ReleaseDialog(FullScreenTouchDialog):
    """Details and release notes for one selected firmware release."""

    install_confirmed = pyqtSignal(dict)

    def __init__(self, release, current_ver, parent):
        super().__init__(release.get("tag") or release.get("version"), parent)
        self.release = release

        vbox = QVBoxLayout()
        vbox.setSpacing(6)
        vbox.setContentsMargins(6, 6, 6, 6)

        text = QTextEdit()
        text.setObjectName("tinylabel")
        text.setReadOnly(True)
        text.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        QScroller.grabGesture(text.viewport(), QScroller.LeftMouseButtonGesture)

        cmp_val = release.get("cmp")
        if cmp_val == 1:
            rel_state = QCoreApplication.translate("Release", "Newer update")
            btn_text = QCoreApplication.translate("Release", "Install update")
        elif cmp_val == 0:
            rel_state = QCoreApplication.translate("Release", "Currently installed")
            btn_text = QCoreApplication.translate("Release", "Reinstall")
        elif cmp_val == -1:
            rel_state = QCoreApplication.translate("Release", "Older version")
            btn_text = QCoreApplication.translate("Release", "Downgrade")
        else:
            rel_state = QCoreApplication.translate("Release", "Custom build")
            btn_text = QCoreApplication.translate("Release", "Install")

        lines = [
            f"<b><font color='#fcce04'>{html.escape(QCoreApplication.translate('Release', 'Version'))}:</font></b> {html.escape(release.get('version') or '-')} ({html.escape(rel_state)})",
            f"<b><font color='#fcce04'>{html.escape(QCoreApplication.translate('Release', 'Installed'))}:</font></b> {html.escape(current_ver or '-')}",
        ]
        if release.get("prerelease"):
            lines.append(f"<b><font color='#fcce04'>{html.escape(QCoreApplication.translate('Release', 'Channel'))}:</font></b> Pre-Release")
        size_str = format_size_mb(release.get("size"))
        if size_str:
            lines.append(f"<b><font color='#fcce04'>{html.escape(QCoreApplication.translate('Release', 'Size'))}:</font></b> {html.escape(size_str)}")
        if release.get("published"):
            lines.append(f"<b><font color='#fcce04'>{html.escape(QCoreApplication.translate('Release', 'Date'))}:</font></b> {html.escape(release['published'])}")
        if release.get("notes"):
            safe_notes = html.escape(release["notes"]).replace("\n", "<br>")
            lines.append(f"<br><b><font color='#fcce04'>{html.escape(QCoreApplication.translate('Release', 'Notes'))}:</font></b><br>{safe_notes}")

        text.setHtml("<br>".join(lines))
        vbox.addWidget(text)

        install_btn = QPushButton(btn_text)
        install_btn.setObjectName("smallerlabel")
        install_btn.clicked.connect(self.on_install_clicked)
        vbox.addWidget(install_btn)

        self.centralWidget.setLayout(vbox)

    def on_install_clicked(self):
        box = TouchMessageBox(QCoreApplication.translate("Release", "Confirm"), self)
        box.addConfirm()
        box.setCancelButton()
        ver = self.release.get("version") or self.release.get("tag")
        if self.release.get("cmp") == -1:
            msg = QCoreApplication.translate(
                "Release",
                "Downgrade to %s?\nCurrent system is backed up to system-old.",
            ) % ver
        else:
            msg = QCoreApplication.translate(
                "Release",
                "Install firmware %s?\nCurrent system is backed up to system-old.",
            ) % ver
        box.setText(msg)
        box.setTextSize(2)
        box.setBtnTextSize(2)
        yes_lbl = QCoreApplication.translate("Release", "Install")
        no_lbl = QCoreApplication.translate("Release", "No")
        box.setPosButton(yes_lbl)
        box.setNegButton(no_lbl)
        ok, choice = box.exec_()
        if ok and choice != no_lbl:
            self.close()
            self.install_confirmed.emit(self.release)


class UpdatePlugin(LauncherPlugin):
    """Main System Update launcher plugin / standalone app."""

    def __init__(self, application):
        super().__init__(application)

        self.translator = QTranslator()
        self.translator.load(self.locale(), os.path.join(APP_DIR, "update_"))
        self.installTranslator(self.translator)

        self.current_version = read_current_version()
        self.source = load_saved_source()
        self.fetch_thread = None
        self.busy = None
        self.detail_dialog = None
        self.install_dialog = None

        self.mainWindow = TouchWindow(QCoreApplication.translate("Update", "System Update"))
        self.menu = self.mainWindow.addMenu()
        self.menu.aboutToShow.connect(self.on_menu_about_to_show)

        act_search = self.menu.addAction(QCoreApplication.translate("Menu", "Search updates"))
        act_search.triggered.connect(self.start_search)

        act_source = self.menu.addAction(QCoreApplication.translate("Menu", "Change source..."))
        act_source.triggered.connect(self.on_change_source)

        self.act_restore = self.menu.addAction(QCoreApplication.translate("Menu", "Restore backup"))
        self.act_restore.triggered.connect(self.on_restore_backup)

        self.menu.addSeparator()
        act_reboot = self.menu.addAction(QCoreApplication.translate("Menu", "Reboot TXT"))
        act_reboot.triggered.connect(self.confirm_reboot)

        vbox = QVBoxLayout()
        vbox.setSpacing(4)
        vbox.setContentsMargins(4, 4, 4, 4)

        self.ver_label = QLabel()
        self.ver_label.setObjectName("smallerlabel")
        vbox.addWidget(self.ver_label)

        self.source_label = QLabel()
        self.source_label.setObjectName("tinylabel")
        self.source_label.setWordWrap(True)
        vbox.addWidget(self.source_label)

        self.status_label = QLabel("")
        self.status_label.setObjectName("tinylabel")
        self.status_label.setWordWrap(True)
        vbox.addWidget(self.status_label)

        self.list_w = QListWidget()
        self.list_w.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        QScroller.grabGesture(self.list_w.viewport(), QScroller.LeftMouseButtonGesture)
        self.list_w.setViewMode(QListView.ListMode)
        self.list_w.setMovement(QListView.Static)
        self.list_w.setIconSize(QSize(24, 24))
        self.list_w.setStyleSheet(
            "QListWidget { background-color: rgba(0,0,0,0); alternate-background-color: rgba(0,0,0,16); font-size: 16px; color: white; }"
            "QListWidget::item { padding: 4px 2px; }"
        )
        self.list_w.itemClicked.connect(self.on_release_clicked)
        vbox.addWidget(self.list_w)

        self.search_btn = QPushButton(QCoreApplication.translate("Update", "Search updates"))
        self.search_btn.setObjectName("smallerlabel")
        self.search_btn.clicked.connect(self.start_search)
        vbox.addWidget(self.search_btn)

        self.mainWindow.centralWidget.setLayout(vbox)
        self.refresh_header()
        self.mainWindow.show()

        QTimer.singleShot(150, self.start_search)

    def exit(self):
        if self.fetch_thread:
            try:
                self.fetch_thread.finished_ok.disconnect()
                self.fetch_thread.finished_err.disconnect()
            except TypeError:
                pass
            if self.fetch_thread.isRunning():
                self.fetch_thread.wait(500)
        super().exit()

    def refresh_header(self):
        ver = self.current_version or "-"
        self.ver_label.setText(QCoreApplication.translate("Update", "Installed: %s") % ver)
        self.source_label.setText(QCoreApplication.translate("Update", "Source: %s") % self.source)

    def _set_busy(self, active):
        self.search_btn.setEnabled(not active)
        if active:
            self.mainWindow.centralWidget.setGraphicsEffect(QGraphicsBlurEffect(self.mainWindow))
            self.busy = BusyAnimation(self.mainWindow)
            self.busy.show()
        else:
            if self.busy:
                self.busy.close()
                self.busy = None
            self.mainWindow.centralWidget.setGraphicsEffect(None)

    def start_search(self):
        if self.fetch_thread and self.fetch_thread.isRunning():
            return
        self.list_w.clear()
        self.status_label.setText(QCoreApplication.translate("Update", "Checking for updates..."))
        self._set_busy(True)
        self.fetch_thread = ReleaseFetchThread(self.source, self.current_version)
        self.fetch_thread.finished_ok.connect(self.on_search_ok)
        self.fetch_thread.finished_err.connect(self.on_search_err)
        self.fetch_thread.start()

    def on_search_ok(self, releases):
        self._set_busy(False)
        if not releases:
            self.status_label.setText(QCoreApplication.translate("Update", "No firmware releases found."))
            return

        newer_count = sum(1 for r in releases if r.get("cmp") == 1)
        if newer_count > 0:
            self.status_label.setText(QCoreApplication.translate("Update", "%d update(s) available") % newer_count)
        else:
            self.status_label.setText(QCoreApplication.translate("Update", "System is up to date"))

        for rel in releases:
            cmp_val = rel.get("cmp")
            if cmp_val == 1:
                icon_file = "rel_update.png"
            elif cmp_val == 0:
                icon_file = "rel_current.png"
            else:
                icon_file = "rel_older.png"

            label = rel.get("version") or rel.get("tag")
            if rel.get("prerelease"):
                label += " [Pre]"
            size_str = format_size_mb(rel.get("size"))
            if size_str:
                label += f" ({size_str})"

            item = QListWidgetItem(QIcon(os.path.join(APP_DIR, icon_file)), label)
            item.setData(Qt.UserRole, rel)
            self.list_w.addItem(item)

    def on_search_err(self, err_msg):
        self._set_busy(False)
        self.status_label.setText(QCoreApplication.translate("Error", "Error: %s") % err_msg)

    def on_release_clicked(self, item):
        release = item.data(Qt.UserRole)
        if not release:
            return
        self.detail_dialog = ReleaseDialog(release, self.current_version, self.mainWindow)
        self.detail_dialog.install_confirmed.connect(self.start_install)
        self.detail_dialog.show()

    def start_install(self, release):
        self.install_dialog = InstallDialog("install", release, self.mainWindow)
        self.install_dialog.reboot_requested.connect(self.perform_reboot)
        self.install_dialog.exec_()

    def on_change_source(self):
        dialog = SourceDialog(self.source, self.mainWindow)
        dialog.source_saved.connect(self.on_source_saved)
        dialog.exec_()

    def on_source_saved(self, new_source):
        save_source(new_source)
        self.source = new_source
        self.refresh_header()
        self.start_search()

    def on_menu_about_to_show(self):
        self.act_restore.setEnabled(os.path.isfile(BOOT_BACKUP_MARKER))

    def on_restore_backup(self):
        if not os.path.isfile(BOOT_BACKUP_MARKER):
            return
        box = TouchMessageBox(QCoreApplication.translate("Install", "Restore backup"), self.mainWindow)
        box.addConfirm()
        box.setCancelButton()
        box.setText(QCoreApplication.translate("Install", "Restore previous system from system-old backup?"))
        box.setTextSize(2)
        box.setBtnTextSize(2)
        yes_lbl = QCoreApplication.translate("Install", "Restore")
        no_lbl = QCoreApplication.translate("Release", "No")
        box.setPosButton(yes_lbl)
        box.setNegButton(no_lbl)
        ok, choice = box.exec_()
        if ok and choice != no_lbl:
            self.install_dialog = InstallDialog("restore", None, self.mainWindow)
            self.install_dialog.reboot_requested.connect(self.perform_reboot)
            self.install_dialog.exec_()

    def confirm_reboot(self):
        box = TouchMessageBox(QCoreApplication.translate("Install", "Reboot TXT"), self.mainWindow)
        box.addConfirm()
        box.setCancelButton()
        box.setText(QCoreApplication.translate("Install", "Reboot the TXT now?"))
        box.setTextSize(2)
        box.setBtnTextSize(2)
        yes_lbl = QCoreApplication.translate("Install", "Reboot")
        no_lbl = QCoreApplication.translate("Release", "No")
        box.setPosButton(yes_lbl)
        box.setNegButton(no_lbl)
        ok, choice = box.exec_()
        if ok and choice != no_lbl:
            self.perform_reboot()

    def perform_reboot(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.settimeout(1.0)
            sock.connect(("localhost", 9000))
            sock.sendall(b"msg Rebooting...\n")
        except OSError:
            pass
        finally:
            sock.close()
        subprocess.Popen(["sudo", "-n", "/sbin/reboot"])


if __name__ == "__main__":
    class FtcGuiApplication(TouchApplication):
        def __init__(self, args):
            super().__init__(args)
            self.module = UpdatePlugin(self)
            self.exec_()

    FtcGuiApplication(sys.argv)
else:
    def createPlugin(launcher):
        return UpdatePlugin(launcher)
