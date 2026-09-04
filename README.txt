EDF3 English Patch Builder 0.1.1
================================

This application creates an English LayerFS mod for Earth Defense Force 3 on
Nintendo Switch. It contains no game, ROM, encryption key, or prebuilt mod
asset. You must supply your own legally dumped games and keys.

QUICK START

1. Extract the entire ZIP to a normal folder.
2. Double-click "EDF3 English Patch Builder.exe".
3. Select:
   - the Japanese Switch base NSP or XCI;
   - the optional v196608 update NSP or XCI;
   - prod.keys dumped from your Switch;
   - US Vita EDF 2017 Portable (PCSE00209), as a folder, ZIP, or VPK;
   - an output folder.
4. If the Vita dump is encrypted, enter its 32-character klicensee. The app
   reads it automatically when sce_sys/package/work.bin is present.
5. Click Build English Mod. The first build can take a while.

The finished package is OUTPUT\EDF3_English. Open its INSTALL.txt for exact
Atmosphere, Ryujinx, and yuzu-compatible LayerFS paths.

SUPPORTED SOURCE VERSIONS

- Switch: 0100E87013C98000 Japanese base v0
- Switch update: 0100E87013C98800 v196608 (optional)
- Vita: PCSE00209 US

The app verifies extracted source content with SHA-1 before creating a patch.
An outer NSP can legitimately have a different hash if it was repacked; its
extracted Program NCA is still checked strictly.

PRIVACY AND DISK USE

The app does not upload ROMs or keys. Encrypted Vita decryption uses the public
F00D compatibility service at cma.henkaku.xyz. Decrypted working files remain
in OUTPUT\.edf3-build-cache so a rebuild is faster; delete that directory when
you no longer need it. Expect several gigabytes of temporary disk use.

The builder never modifies the selected source files.
