import ctypes
import hashlib
import os
import re
import shutil
import sys
import zipfile
from pathlib import Path


def _vider_cache_client_flet() -> None:
    if sys.platform != "win32" or not getattr(sys, "frozen", False):
        return
    cache = Path.home() / ".flet" / "client"
    if cache.is_dir():
        shutil.rmtree(cache, ignore_errors=True)


def _deployer_client_embarque() -> None:
    if sys.platform != "win32" or not getattr(sys, "frozen", False):
        return

    meipass = getattr(sys, "_MEIPASS", None)
    if not meipass:
        return

    archive = Path(meipass) / "flet_desktop" / "app" / "flet-windows.zip"
    if not archive.is_file():
        return

    base = Path(sys.executable).resolve().parent / ".flet_runtime"
    flet_exe = base / "flet" / "flet.exe"
    rebuild = not flet_exe.is_file()
    if flet_exe.is_file() and archive.stat().st_mtime > flet_exe.stat().st_mtime:
        rebuild = True

    if rebuild:
        shutil.rmtree(base, ignore_errors=True)
        base.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(base)

    os.environ["FLET_VIEW_PATH"] = str(base / "flet")


def definir_app_user_model_id() -> None:
    if sys.platform != "win32" or not getattr(sys, "frozen", False):
        return

    exe_path = os.path.abspath(sys.executable)
    exe_stem = os.path.splitext(os.path.basename(exe_path))[0]
    safe_name = re.sub(r"[^A-Za-z0-9]", "", exe_stem)[:64] or "App"
    path_hash = hashlib.sha1(exe_path.encode("utf-8")).hexdigest()[:16]
    os.environ["FLET_APP_USER_MODEL_ID"] = f"Flet.{safe_name}.{path_hash}"


def _appliquer_aumid_processus_parent() -> None:
    aumid = os.environ.get("FLET_APP_USER_MODEL_ID")
    if not aumid:
        return
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(aumid)
    except OSError:
        pass


def preparer_windows_packagine() -> None:
    _vider_cache_client_flet()
    definir_app_user_model_id()
    _deployer_client_embarque()
    _appliquer_aumid_processus_parent()
