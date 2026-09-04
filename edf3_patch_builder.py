"""User-friendly builder for the EDF3 Nintendo Switch English LayerFS mod.

Run without arguments for the Windows GUI, or use --cli for automation.
The builder never modifies the supplied games and never includes game assets in
its own distribution; users must provide their legally dumped copies.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TITLE_ID = "0100E87013C98000"
KNOWN_SHA1 = {
    "switch_base_nsp": "f3d67f71639865cdc07558d6919d4f7265fbc2ff",
    "switch_update_nsp": "968f410637d2ba226f80c11c03aac3b7f4956338",
    "switch_base_program_nca": "a65cc13d734539ae39af221b9c1edede4f1c87ae",
    "switch_update_program_nca": "339058b44ca79dbd539b9bcfc7ee6e232a7dfb5a",
    # Hash after PFS decryption. The encrypted NoNpDrm file has the same size
    # but different bytes (FFC087...), so checking it here rejects valid dumps.
    "vita_data_psarc": "40d4fb476dd91cdd8ba39efdcc68ab9a5ff8a445",
    "vita_voice_dpk": "9fdd43fde25d1f7442a50df93c2af3a164b5f754",
}


class BuildError(RuntimeError):
    pass


# The GUI is launched through pythonw.exe. Without this flag, every hactool,
# FFmpeg, and encoder child briefly creates a console window on Windows.
NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0


def log_line(callback, text):
    callback(str(text))


def redact(text):
    text = re.sub(r"--titlekey=[0-9A-Fa-f]+", "--titlekey=[redacted]", text)
    if "titlekey" in text.lower():
        return "[title key output redacted]"
    return text


def run(command, callback, env=None):
    log_line(callback, redact("> " + subprocess.list2cmdline([str(x) for x in command])))
    process = subprocess.Popen(
        [str(x) for x in command], cwd=ROOT, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding="utf-8", errors="replace",
        creationflags=NO_WINDOW,
    )
    assert process.stdout
    saved = 0
    for line in process.stdout:
        clean = line.rstrip()
        if clean.lstrip().startswith("Saving "):
            saved += 1
            if saved % 250 == 0:
                log_line(callback, f"  extracted {saved} files...")
            continue
        log_line(callback, redact(clean))
    process.stdout.close()
    code = process.wait()
    if code:
        raise BuildError(f"Command failed with exit code {code}: {command[0]}")


def tool(relative):
    path = ROOT / relative
    if not path.is_file():
        raise BuildError(f"Required tool is missing: {path}")
    return path


def ffmpeg_path():
    bundled = ROOT / "tools/ffmpeg/ffmpeg.exe"
    if bundled.is_file():
        return bundled
    found = shutil.which("ffmpeg")
    return Path(found) if found else None


def sha1_file(path, chunk_size=8 * 1024 * 1024):
    digest = hashlib.sha1()
    with open(path, "rb") as source:
        while True:
            chunk = source.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def verify_sha1(path, expected, label, callback):
    log_line(callback, f"SHA-1 checking {label}...")
    actual = sha1_file(path)
    log_line(callback, f"  {actual}  {path.name}")
    if actual.lower() != expected.lower():
        raise BuildError(
            f"{label} SHA-1 mismatch. Expected {expected}, got {actual}. "
            "The dump is corrupted or is the wrong region/version."
        )
    return actual


def check_container_sha1(path, expected, label, callback):
    """Report an outer-container hash; content hashes remain authoritative."""
    log_line(callback, f"SHA-1 checking {label}...")
    actual = sha1_file(path)
    log_line(callback, f"  {actual}  {path.name}")
    if actual.lower() != expected.lower():
        log_line(callback, "  Outer container differs from the reference dump; extracted content will be verified.")
        return False
    log_line(callback, "  Exact reference container match.")
    return True


def safe_extract_zip(source, destination):
    root = destination.resolve()
    with zipfile.ZipFile(source) as archive:
        for member in archive.infolist():
            target = (destination / member.filename).resolve()
            try:
                target.relative_to(root)
            except ValueError:
                raise BuildError(f"Unsafe path in Vita archive: {member.filename}")
        archive.extractall(destination)


def sanitized_keys(source, destination):
    lines = []
    for raw in source.read_text(encoding="utf-8", errors="ignore").splitlines():
        match = re.match(r"^\s*([A-Za-z0-9_]+)\s*=\s*([0-9A-Fa-f]+)\s*$", raw)
        if match and len(match.group(2)) in (32, 64):
            lines.append(f"{match.group(1)} = {match.group(2).lower()}")
    if not lines:
        raise BuildError("The selected prod.keys file contains no usable keys.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(lines) + "\n", encoding="ascii")


def unpack_switch_container(image, destination, hactool, keys, callback):
    destination.mkdir(parents=True, exist_ok=True)
    suffix = image.suffix.lower()
    if suffix == ".nsp":
        run([hactool, "-k", keys, "--disablekeywarns", "-t", "pfs0",
             f"--outdir={destination}", image], callback)
    elif suffix == ".xci":
        run([hactool, "-k", keys, "--disablekeywarns", "-t", "xci",
             f"--securedir={destination}", image], callback)
    else:
        raise BuildError("Switch input must be an NSP or XCI dump.")


def nca_info(path, hactool, keys):
    result = subprocess.run(
        [str(hactool), "-k", str(keys), "--disablekeywarns", "-t", "nca", "-i", str(path)],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
        creationflags=NO_WINDOW,
    )
    return result.stdout + result.stderr


def find_program_nca(folder, hactool, keys, expected_title):
    candidates = sorted(folder.rglob("*.nca"), key=lambda p: p.stat().st_size, reverse=True)
    for path in candidates:
        info = nca_info(path, hactool, keys)
        if "Content Type:" in info and "Program" in info and expected_title.lower() in info.lower():
            return path
    raise BuildError(f"Could not find the EDF3 Program NCA ({expected_title}) in {folder}.")


def ticket_title_key(folder):
    tickets = list(folder.rglob("*.tik"))
    if not tickets:
        return None
    data = tickets[0].read_bytes()
    if len(data) < 0x190:
        raise BuildError(f"Ticket is too small: {tickets[0]}")
    return data[0x180:0x190].hex()


def extract_switch(base, update, keys_source, work, callback):
    hactool = tool("tools/hactool/hactool.exe")
    switch = work / "switch"
    clean_keys = switch / "hactool.keys"
    sanitized_keys(keys_source, clean_keys)

    if base.suffix.lower() == ".nsp":
        check_container_sha1(base, KNOWN_SHA1["switch_base_nsp"], "Switch base NSP", callback)

    base_files = switch / "base_nsp"
    base_romfs = switch / "base_romfs"
    marker = base_romfs / "JP/MainSequence/text.sgo"
    if not marker.is_file():
        log_line(callback, "Extracting the Switch base game (this may take several minutes)...")
        unpack_switch_container(base, base_files, hactool, clean_keys, callback)
        base_nca = find_program_nca(base_files, hactool, clean_keys, TITLE_ID)
        run([hactool, "-k", clean_keys, "--disablekeywarns", "-t", "nca",
             f"--romfsdir={base_romfs}", base_nca], callback)
    else:
        log_line(callback, "Using cached Switch base extraction.")
        base_nca = find_program_nca(base_files, hactool, clean_keys, TITLE_ID)
    verify_sha1(base_nca, KNOWN_SHA1["switch_base_program_nca"], "Switch base Program NCA", callback)
    if not marker.is_file():
        raise BuildError("The extracted Switch image is not EDF3 or its RomFS could not be decrypted.")

    if not update:
        return base_romfs

    update_files = switch / "update_nsp"
    update_romfs = switch / "update_romfs"
    update_marker = update_romfs / "JP/Weapon/weapontext.sgo"
    if update.suffix.lower() == ".nsp":
        check_container_sha1(update, KNOWN_SHA1["switch_update_nsp"], "Switch v196608 update NSP", callback)
    if not update_marker.is_file():
        log_line(callback, "Extracting and merging the optional Switch update...")
        unpack_switch_container(update, update_files, hactool, clean_keys, callback)
        update_nca = find_program_nca(update_files, hactool, clean_keys, TITLE_ID[:-3] + "800")
        command = [hactool, "-k", clean_keys, "--disablekeywarns", "-t", "nca",
                   f"--basenca={base_nca}", f"--romfsdir={update_romfs}"]
        title_key = ticket_title_key(update_files)
        if title_key:
            command.append(f"--titlekey={title_key}")
        command.append(update_nca)
        run(command, callback)
    else:
        update_nca = find_program_nca(update_files, hactool, clean_keys, TITLE_ID[:-3] + "800")
    verify_sha1(update_nca, KNOWN_SHA1["switch_update_program_nca"], "Switch update Program NCA", callback)
    if not update_marker.is_file():
        raise BuildError("The Switch update could not be merged with the selected base game.")
    return update_romfs


def locate_vita_root(path):
    if (path / "US/data.psarc").is_file():
        return path
    matches = [p.parent.parent for p in path.rglob("US/data.psarc")]
    if len(matches) == 1:
        return matches[0]
    title = path / "app/PCSE00209"
    if title.is_dir():
        return title
    matches = [p for p in path.rglob("PCSE00209") if p.is_dir()]
    return matches[0] if len(matches) == 1 else None


def extract_vita(source, supplied_key, work, callback):
    vita_stage = work / "vita_source"
    if source.is_file():
        if source.suffix.lower() not in (".zip", ".vpk"):
            raise BuildError("Vita input must be a game folder, ZIP, or VPK.")
        if not vita_stage.exists():
            log_line(callback, "Unpacking the Vita archive...")
            vita_stage.mkdir(parents=True)
            safe_extract_zip(source, vita_stage)
        source_root = vita_stage
    else:
        source_root = source

    vita_root = locate_vita_root(source_root)
    if not vita_root:
        raise BuildError("Could not find PCSE00209 or US/data.psarc in the Vita input.")

    decrypted = work / "vita_dec" / "app"
    if (vita_root / "US/data.psarc").is_file() and not (vita_root / "sce_pfs").exists():
        decrypted = vita_root
        log_line(callback, "Vita input appears to be decrypted; skipping PFS decryption.")
    elif not (decrypted / "US/data.psarc").is_file():
        key = supplied_key.strip()
        if not key:
            work_bin = vita_root / "sce_sys/package/work.bin"
            if not work_bin.is_file():
                raise BuildError("Encrypted Vita input requires a 32-hex klicensee or sce_sys/package/work.bin.")
            data = work_bin.read_bytes()
            if len(data) < 0x60:
                raise BuildError("Vita work.bin is invalid.")
            key = data[0x50:0x60].hex()
            log_line(callback, "Read the Vita klicensee from work.bin.")
        if not re.fullmatch(r"[0-9A-Fa-f]{32}", key):
            raise BuildError("Vita klicensee must contain exactly 32 hexadecimal characters.")
        parser = tool("tools/psvpfstools/release_win64_7/psvpfsparser.exe")
        log_line(callback, "Decrypting the Vita game...")
        run([parser, "-i", vita_root, "-o", decrypted, "-k", key,
             "-f", "http://cma.henkaku.xyz"], callback)

    psarc = decrypted / "US/data.psarc"
    if not psarc.is_file():
        raise BuildError("Vita decryption finished without producing US/data.psarc.")
    verify_sha1(psarc, KNOWN_SHA1["vita_data_psarc"], "Vita US data.psarc", callback)
    unpacked = work / "vita_dec" / "psarc"
    marker = unpacked / "MainSequence/text.sgo"
    if not marker.is_file():
        log_line(callback, "Unpacking the Vita data archive...")
        run([sys.executable, tool("tools/scripts/psarc.py"), psarc, unpacked], callback)
    if not marker.is_file():
        raise BuildError("The Vita archive is not the US EDF 2017 Portable data set.")
    verify_sha1(unpacked / "Sound/Voice/Sound_Sgo.dpk", KNOWN_SHA1["vita_voice_dpk"],
                "Vita English voice bank", callback)


def write_install_instructions(mod_root):
    text = f"""EDF3 English translation mod
Title ID: {TITLE_ID}

The generated romfs folder is ready for LayerFS.

Eden / yuzu:
  %APPDATA%\\yuzu\\load\\{TITLE_ID}\\EDF3_English\\romfs

Ryujinx:
  %APPDATA%\\Ryujinx\\mods\\contents\\{TITLE_ID.lower()}\\EDF3_English\\romfs

Atmosphere:
  sd:/atmosphere/contents/{TITLE_ID}/romfs

Copy this package's romfs directory to the matching location. Replace an older
EDF3 English mod completely so stale files cannot remain. The v196608 update is
supported when supplied to the builder; a base-only build uses the base stats.
"""
    (mod_root / "INSTALL.txt").write_text(text, encoding="utf-8")


def build(args, callback=print):
    base = Path(args.switch).expanduser().resolve()
    update = Path(args.update).expanduser().resolve() if args.update else None
    keys = Path(args.keys).expanduser().resolve()
    vita = Path(args.vita).expanduser().resolve()
    destination = Path(args.output).expanduser().resolve()
    for label, path in (("Switch game", base), ("prod.keys", keys), ("Vita game", vita)):
        if not path.exists():
            raise BuildError(f"{label} does not exist: {path}")
    if update and not update.exists():
        raise BuildError(f"Switch update does not exist: {update}")
    ffmpeg = ffmpeg_path()
    if ffmpeg is None:
        raise BuildError("ffmpeg is required for voice conversion and was not found in the app or PATH.")

    work = Path(args.work_dir).expanduser().resolve() if args.work_dir else destination / ".edf3-build-cache"
    mod_root = destination / "EDF3_English"
    romfs = mod_root / "romfs"
    if romfs.exists():
        if not args.overwrite:
            raise BuildError(f"Output already exists: {romfs}\nEnable overwrite to rebuild it.")
        shutil.rmtree(romfs)
    work.mkdir(parents=True, exist_ok=True)
    romfs.mkdir(parents=True)

    switch_romfs = extract_switch(base, update, keys, work, callback)
    extract_vita(vita, args.vita_key or "", work, callback)

    env = os.environ.copy()
    env["EDF3_WORK_DIR"] = str(work)
    env["EDF3_SWITCH_ROMFS"] = str(switch_romfs)
    env["EDF3_OUTPUT_ROMFS"] = str(romfs)
    env["EDF3_FFMPEG"] = str(ffmpeg)
    steps = [
        "build_patch.py",
        "build_textures.py",
        "build_controller_textures.py",
        "audio_build.py",
        "verify_patch.py",
    ]
    for script in steps:
        log_line(callback, f"Running {script}...")
        run([sys.executable, tool("tools/scripts/" + script)], callback, env=env)
    write_install_instructions(mod_root)
    log_line(callback, "BUILD COMPLETE")
    log_line(callback, f"Install-ready mod: {mod_root}")
    return mod_root


def parser():
    p = argparse.ArgumentParser(description="Build the EDF3 Switch English LayerFS mod")
    p.add_argument("--cli", action="store_true", help="use command-line mode")
    p.add_argument("--switch", help="EDF3 Switch base NSP or XCI")
    p.add_argument("--update", help="optional v196608 update NSP/XCI")
    p.add_argument("--keys", help="Switch prod.keys")
    p.add_argument("--vita", help="EDF 2017 Portable US game folder, ZIP, or VPK")
    p.add_argument("--vita-key", default="", help="optional 32-hex klicensee; auto-read from work.bin")
    p.add_argument("--output", help="directory that will receive EDF3_English")
    p.add_argument("--work-dir", help="optional persistent extraction/cache directory")
    p.add_argument("--overwrite", action="store_true", help="replace an existing generated romfs")
    return p


def gui():
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    root = tk.Tk()
    root.title("EDF3 English Patch Builder")
    root.geometry("820x650")
    root.minsize(720, 560)
    values = {name: tk.StringVar() for name in ("switch", "update", "keys", "vita", "vita_key", "output")}
    messages = queue.Queue()

    outer = ttk.Frame(root, padding=14); outer.pack(fill="both", expand=True)
    ttk.Label(outer, text="EDF3 English Patch Builder", font=("Segoe UI", 17, "bold")).pack(anchor="w")
    ttk.Label(outer, text="Supply your own legally dumped games. No game data is distributed with this builder.").pack(anchor="w", pady=(2, 12))
    form = ttk.Frame(outer); form.pack(fill="x")

    def row(label, key, mode="file", optional=False):
        line = ttk.Frame(form); line.pack(fill="x", pady=3)
        ttk.Label(line, text=label + (" (optional)" if optional else ""), width=27).pack(side="left")
        ttk.Entry(line, textvariable=values[key]).pack(side="left", fill="x", expand=True, padx=6)
        def browse():
            if mode in ("dir", "vita"): selected = filedialog.askdirectory()
            else: selected = filedialog.askopenfilename()
            if selected: values[key].set(selected)
        ttk.Button(line, text="Browse…", command=browse).pack(side="right")
        if mode == "vita":
            def archive():
                selected = filedialog.askopenfilename(filetypes=[("Vita archives", "*.zip *.vpk"), ("All files", "*.*")])
                if selected: values[key].set(selected)
            ttk.Button(line, text="Archive…", command=archive).pack(side="right", padx=(0, 4))

    row("Switch base NSP/XCI", "switch")
    row("Switch update NSP/XCI", "update", optional=True)
    row("Switch prod.keys", "keys")
    row("Vita US folder/ZIP/VPK", "vita", mode="vita")
    ttk.Label(form, text="For a Vita folder, paste its path directly or choose any file inside it.").pack(anchor="w", padx=220)
    row("Vita klicensee", "vita_key", optional=True)
    row("Output directory", "output", mode="dir")

    options = ttk.Frame(outer); options.pack(fill="x", pady=(8, 4))
    overwrite = tk.BooleanVar(value=True)
    ttk.Checkbutton(options, text="Replace an existing generated EDF3_English/romfs", variable=overwrite).pack(side="left")
    progress = ttk.Progressbar(outer, mode="indeterminate"); progress.pack(fill="x", pady=6)
    output = tk.Text(outer, height=18, wrap="word", state="disabled", font=("Consolas", 9)); output.pack(fill="both", expand=True)
    buttons = ttk.Frame(outer); buttons.pack(fill="x", pady=(8, 0))

    def append(text):
        output.configure(state="normal"); output.insert("end", text + "\n"); output.see("end"); output.configure(state="disabled")

    def poll():
        try:
            while True:
                kind, payload = messages.get_nowait()
                if kind == "log": append(payload)
                else:
                    progress.stop(); build_button.configure(state="normal")
                    if kind == "done": messagebox.showinfo("Build complete", f"Install-ready mod:\n{payload}")
                    else: messagebox.showerror("Build failed", payload)
        except queue.Empty:
            pass
        root.after(100, poll)

    def start():
        required = ("switch", "keys", "vita", "output")
        if any(not values[k].get().strip() for k in required):
            messagebox.showerror("Missing input", "Select the Switch game, prod.keys, Vita game, and output directory.")
            return
        ns = argparse.Namespace(**{k: v.get().strip() for k, v in values.items()},
                                cli=False, work_dir=None, overwrite=overwrite.get())
        build_button.configure(state="disabled"); progress.start(10); append("Starting build...")
        def worker():
            try:
                result = build(ns, lambda line: messages.put(("log", line)))
                messages.put(("done", str(result)))
            except Exception as exc:
                messages.put(("error", str(exc)))
        threading.Thread(target=worker, daemon=True).start()

    build_button = ttk.Button(buttons, text="Build English Mod", command=start); build_button.pack(side="right")
    ttk.Button(buttons, text="Exit", command=root.destroy).pack(side="right", padx=8)
    poll(); root.mainloop()


def main():
    # Windows commonly starts Python with a legacy console code page. Build
    # diagnostics may contain Japanese paths, so never let console encoding
    # terminate an otherwise valid build.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    p = parser(); args = p.parse_args()
    if not args.cli and not any((args.switch, args.keys, args.vita, args.output)):
        gui(); return
    missing = [name for name in ("switch", "keys", "vita", "output") if not getattr(args, name)]
    if missing:
        p.error("required in CLI mode: " + ", ".join("--" + x for x in missing))
    try:
        build(args)
    except BuildError as exc:
        print("ERROR:", exc, file=sys.stderr); raise SystemExit(1)


if __name__ == "__main__":
    main()
