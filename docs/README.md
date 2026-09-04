# Documentation index

## Distributable patch builder

The public Windows application is built with `build_release.bat`. It creates
`dist/EDF3-English-Patch-Builder-v0.1.1.zip`, containing a double-clickable GUI,
its portable Python/Pillow runtime, FFmpeg, and the required extraction tools.
The packager uses an explicit allowlist and fails if a ROM, NCA, ticket,
`prod.keys`, `title.keys`, Vita archive, or `work.bin` reaches the application
folder. End users only need to extract the ZIP and run
`EDF3 English Patch Builder.exe`; `README.txt` contains the complete workflow.

The app verifies the supported Switch Program NCAs, the PFS-decrypted Vita
`data.psarc`, and its English voice bank by SHA-1 before building. Outer NSP
hashes are advisory because a legal dump may be repacked without changing the
strictly checked Program NCA.

Related working notes: `work/tex/report.md` (texture survey) and
`work/audio/voice_review.csv` (voice line mapping).
