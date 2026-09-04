# EDF3 English Patch Builder


Source code for the Windows application that builds the English LayerFS patch
for the Japanese Nintendo Switch release of *Earth Defense Force 3* from the
user's own supported Switch and US PlayStation Vita dumps.

No ROMs, game keys, decrypted game files, generated LayerFS files, or audio are
included in this repository. You have to bring your own roms and keys.

No game script, dialogue, or localized text is included either. The English
text is read out of your own Vita dump while the patch is built; this
repository only stores the index maps that place each source string in the
right slot, plus a handful of strings written for this project to cover Switch
UI that has no Vita counterpart.

## Running from source

Requirements: Windows 10/11, Python 3.11+, and Pillow.

```bat
python -m pip install -r requirements.txt
python edf3_patch_builder.py
```

FFmpeg must be available in `PATH` for source runs. The application also
expects the helper executables already included under `tools/`.

## Tests

```bat
run_tests.bat
```

Integration inventory checks are skipped when a locally built `patch/romfs`
is not present. No proprietary input is required for the format and safety
unit tests.

## Building the portable application

Install FFmpeg in `PATH`, then run:

```bat
build_release.bat
```

The release assembler creates a ROM-free ZIP under `dist/`, bundles a local
Python/Pillow runtime, and fails its audit if it finds common ROM, ticket, or
key file types in the release tree.

Supported source versions and SHA-1 behavior are documented in `README.txt`.

## Third-party programs

See `THIRD_PARTY_NOTICES.txt`. FFmpeg is not committed to this source tree; it
is copied from the developer's `PATH` only while assembling a binary release.
