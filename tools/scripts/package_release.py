"""Create the redistributable, ROM-free Windows patch-builder application."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import PIL

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "dist"
VERSION = "0.1.1"
APP = DIST / f"EDF3-English-Patch-Builder-v{VERSION}"

SCRIPTS = (
    "audio_build.py", "audio_encode.py", "build_controller_textures.py",
    "build_patch.py", "build_textures.py", "psarc.py", "sgo.py", "sgsl.py",
    "statmerge.py", "tex_bntx.py", "tex_dxb.py", "tex_vita.py",
    "verify_patch.py", "xmlbin.py",
)
METADATA = (
    "work/audio/voice_review.csv", "work/audio/dpk_index.json",
    "work/tex/report.md", "work/mainseq_map.json",
)


def copy_file(relative: str) -> None:
    source = ROOT / relative
    target = APP / relative
    if not source.is_file():
        raise RuntimeError(f"Required release input is missing: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def ignore_runtime(_folder, names):
    ignored = {"site-packages", "__pycache__", "test", "tests", "idlelib", "ensurepip"}
    return [name for name in names if name in ignored or name.endswith((".pyc", ".pyo"))]


def copy_runtime() -> None:
    base = Path(sys.base_prefix)
    runtime = APP / "runtime"
    runtime.mkdir(parents=True)
    for name in ("python.exe", "pythonw.exe", "python3.dll", "python311.dll",
                 "vcruntime140.dll", "vcruntime140_1.dll", "LICENSE.txt"):
        shutil.copy2(base / name, runtime / name)
    shutil.copytree(base / "DLLs", runtime / "DLLs", ignore=ignore_runtime)
    shutil.copytree(base / "Lib", runtime / "Lib", ignore=ignore_runtime)
    shutil.copytree(base / "tcl", runtime / "tcl", ignore=ignore_runtime)
    pil = Path(PIL.__file__).resolve().parent
    shutil.copytree(pil, runtime / "Lib/site-packages/PIL", ignore=ignore_runtime)


def compile_launcher() -> None:
    source = APP / "packaging/Launcher.cs"
    output = APP / "EDF3 English Patch Builder.exe"
    command = (
        "$ErrorActionPreference='Stop'; "
        f"Add-Type -Path '{source}' -OutputAssembly '{output}' "
        "-OutputType WindowsApplication -ReferencedAssemblies System.Windows.Forms"
    )
    subprocess.run(["powershell", "-NoProfile", "-Command", command], check=True)
    shutil.rmtree(APP / "packaging")


def audit() -> None:
    forbidden_suffixes = {".nsp", ".xci", ".nca", ".tik", ".psarc", ".vpk", ".iso", ".xex"}
    forbidden_names = {"prod.keys", "title.keys", "work.bin", "hactool.keys"}
    bad = []
    for path in APP.rglob("*"):
        if path.is_file() and (path.suffix.lower() in forbidden_suffixes or path.name.lower() in forbidden_names):
            bad.append(str(path.relative_to(APP)))
    if bad:
        raise RuntimeError("Release contains private/game files: " + ", ".join(bad))


def main() -> None:
    if APP.exists():
        shutil.rmtree(APP)
    APP.mkdir(parents=True)
    for relative in ("edf3_patch_builder.py", "README.txt", "THIRD_PARTY_NOTICES.txt"):
        copy_file(relative)
    for script in SCRIPTS:
        copy_file("tools/scripts/" + script)
    for relative in METADATA:
        copy_file(relative)
    for relative in (
        "tools/hactool/hactool.exe", "tools/psvpfstools/release_win64_7/psvpfsparser.exe",
        "tools/psvpfstools/release_win64_7/libcurl.dll",
        "tools/vgaudio/net451_standalone/VGAudioCli.exe", "packaging/Launcher.cs",
    ):
        copy_file(relative)

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required to assemble the self-contained release")
    ffmpeg = str(Path(ffmpeg).resolve())
    target = APP / "tools/ffmpeg/ffmpeg.exe"; target.parent.mkdir(parents=True)
    shutil.copy2(ffmpeg, target)
    ffroot = Path(ffmpeg).parent.parent
    for name in ("LICENSE", "README.txt"):
        if (ffroot / name).is_file():
            shutil.copy2(ffroot / name, target.parent / ("FFmpeg-" + name))

    copy_runtime()
    compile_launcher()
    audit()
    archive = shutil.make_archive(str(DIST / f"EDF3-English-Patch-Builder-v{VERSION}"), "zip", DIST, APP.name)
    print(f"Application: {APP}")
    print(f"Archive: {archive}")
    print(f"Size: {Path(archive).stat().st_size / 1024 / 1024:.1f} MiB")


if __name__ == "__main__":
    main()
