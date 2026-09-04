# Switch EDF3 textures differing from Vita (86 of 379; the other 293 are pixel-identical)

Formats: Switch BC3 0x1c01 (362), BC2 0x1b01 (7), BC7 0x2001 (8); Vita DXT5/DXT3, 3 RGBA8, 4 SGSL-compressed DDS. Vita blocks may be twiddled (see vita_layouts.json).
Summary (86 differing): credits: 26, transferable English textures: 41, title logo: 7, no text; cosmetic difference only — skip: 6, controller/help textures rebuilt with Switch glyphs: 6



| texture | Switch fmt WxH | Vita fmt WxH (layout) | diff | verdict |
|---|---|---|---|---|
| XUI_staff_staff_06_02 | 0x1c01 256x512 | DXT5 512x512 (linear) | 164.77 | credits: different staff lists (Vita lists the US localization team); NOT drop-in — keep JP or make custom [SIZE MISMATCH] |
| XUI_staff_staff_02_01 | 0x1c01 256x128 | DXT5 512x128 (linear) | 162.24 | credits: different staff lists (Vita lists the US localization team); NOT drop-in — keep JP or make custom [SIZE MISMATCH] |
| XUI_staff_staff_06_01 | 0x1c01 256x256 | DXT5 512x256 (linear) | 156.27 | credits: different staff lists (Vita lists the US localization team); NOT drop-in — keep JP or make custom [SIZE MISMATCH] |
| XUI_staff_staff_08_04 | 0x1c01 512x512 | DXT5 512x512 (linear) | 154.10 | credits: different staff lists (Vita lists the US localization team); NOT drop-in — keep JP or make custom |
| XUI_staff_staff_02_03 | 0x1c01 256x512 | DXT5 512x512 (linear) | 146.88 | credits: different staff lists (Vita lists the US localization team); NOT drop-in — keep JP or make custom [SIZE MISMATCH] |
| XUI_staff_staff_09_01 | 0x1c01 256x256 | DXT5 512x256 (linear) | 139.98 | credits: different staff lists (Vita lists the US localization team); NOT drop-in — keep JP or make custom [SIZE MISMATCH] |
| XUI_ed_ed_07_02 | 0x1c01 512x32 | DXT5 1024x32 (linear) | 133.61 | DROP-IN (English text, same layout) [Vita artwork resized to Switch width and re-encoded as DXT5] |
| XUI_staff_staff_08_06 | 0x1c01 256x256 | DXT5 512x256 (linear) | 133.37 | credits: different staff lists (Vita lists the US localization team); NOT drop-in — keep JP or make custom [SIZE MISMATCH] |
| XUI_title_01_title_01_14_01 | 0x1c01 512x256 | DXT3 1024x256 (linear) | 132.47 | title logo: Vita shows "EDF 2017 Portable"; NOT drop-in — keep JP logo or custom art [SIZE MISMATCH] |
| XUI_title_01_title_01_03_01 | 0x1c01 1024x256 | DXT3 1024x512 (linear) | 130.91 | title logo: Vita shows "EDF 2017 Portable"; NOT drop-in — keep JP logo or custom art [SIZE MISMATCH] |
| XUI_staff_staff_08_02 | 0x1c01 512x512 | DXT5 512x512 (linear) | 126.13 | credits: different staff lists (Vita lists the US localization team); NOT drop-in — keep JP or make custom |
| XUI_title_01_title_01_07_02 | 0x1c01 256x256 | RGBA 256x512 (linear) | 125.70 | title logo: Vita shows "EDF 2017 Portable"; NOT drop-in — keep JP logo or custom art [needs BC3 encode: Switch is BC7 / Vita RGBA8] [SIZE MISMATCH] |
| XUI_staff_staff_08_01 | 0x1c01 256x256 | DXT5 256x256 (linear) | 109.36 | credits: different staff lists (Vita lists the US localization team); NOT drop-in — keep JP or make custom |
| XUI_title_01_title_01_07_01 | 0x1c01 1024x256 | RGBA 1024x512 (linear) | 108.66 | title logo: Vita shows "EDF 2017 Portable"; NOT drop-in — keep JP logo or custom art [needs BC3 encode: Switch is BC7 / Vita RGBA8] [SIZE MISMATCH] |
| XUI_staff_staff_08_03 | 0x1c01 512x512 | DXT5 512x512 (linear) | 88.89 | credits: different staff lists (Vita lists the US localization team); NOT drop-in — keep JP or make custom |
| XUI_staff_staff_09_02 | 0x1c01 256x512 | DXT5 512x512 (linear) | 84.57 | credits: different staff lists (Vita lists the US localization team); NOT drop-in — keep JP or make custom [SIZE MISMATCH] |
| XUI_staff_staff_04_01 | 0x1c01 256x512 | DXT5 256x512 (linear) | 83.15 | credits: different staff lists (Vita lists the US localization team); NOT drop-in — keep JP or make custom |
| XUI_loading_normal_loading_02_bg_04_01 | 0x2001 1024x512 | DXT3 1024x512 (linear) | 83.05 | DROP-IN (English text, same layout) [BNTX retagged BC7 to DXT3] |
| XUI_title_01_title_01_15 | 0x1c01 512x512 | RGBA 512x512 (linear) | 80.44 | title logo: Vita shows "EDF 2017 Portable"; NOT drop-in — keep JP logo or custom art [needs BC3 encode: Switch is BC7 / Vita RGBA8] |
| XUI_staff_staff_10_01 | 0x1c01 512x256 | DXT5 256x256 (linear) | 80.41 | credits: different staff lists (Vita lists the US localization team); NOT drop-in — keep JP or make custom [SIZE MISMATCH] |
| XUI_staff_staff_03_02 | 0x1c01 256x256 | DXT5 256x256 (linear) | 75.86 | credits: different staff lists (Vita lists the US localization team); NOT drop-in — keep JP or make custom |
| XUI_staff_staff_11_01 | 0x1c01 256x256 | DXT5 256x256 (linear) | 72.22 | credits: different staff lists (Vita lists the US localization team); NOT drop-in — keep JP or make custom |
| XUI_staff_staff_08_05 | 0x1c01 512x512 | DXT5 512x512 (linear) | 69.77 | credits: different staff lists (Vita lists the US localization team); NOT drop-in — keep JP or make custom |
| XUI_staff_staff_03_01 | 0x1c01 256x512 | DXT5 256x512 (linear) | 67.28 | credits: different staff lists (Vita lists the US localization team); NOT drop-in — keep JP or make custom |
| XUI_title_01_title_01_13 | 0x1c01 1024x32 | DXT5 1024x32 (linear) | 62.65 | title logo: Vita shows "EDF 2017 Portable"; NOT drop-in — keep JP logo or custom art |
| XUI_staff_staff_07_02 | 0x1c01 512x512 | DXT5 512x512 (linear) | 62.16 | credits: different staff lists (Vita lists the US localization team); NOT drop-in — keep JP or make custom |
| XUI_staff_staff_26 | 0x1c01 512x128 | DXT5 512x128 (linear) | 58.20 | credits: different staff lists (Vita lists the US localization team); NOT drop-in — keep JP or make custom |
| XUI_2p_win_2p_win_02 | 0x1c01 1024x128 | DXT5 1024x128 (linear) | 57.86 | DROP-IN (English text, same layout) |
| XUI_4p_win_4p_win_02 | 0x1b01 1024x128 | DXT3 1024x128 (linear) | 57.70 | DROP-IN (English text, same layout) |
| XUI_3p_win_3p_win_02 | 0x1b01 1024x128 | DXT3 1024x128 (linear) | 56.29 | DROP-IN (English text, same layout) |
| XUI_staff_staff_02_02 | 0x1c01 512x256 | DXT5 512x256 (linear) | 55.12 | credits: different staff lists (Vita lists the US localization team); NOT drop-in — keep JP or make custom |
| XUI_1p_win_1p_win_02 | 0x1c01 1024x128 | DXT5 1024x128 (linear) | 54.03 | DROP-IN (English text, same layout) |
| XUI_staff_staff_10_02 | 0x1c01 512x512 | DXT5 512x512 (linear) | 53.96 | credits: different staff lists (Vita lists the US localization team); NOT drop-in — keep JP or make custom |
| XUI_staff_staff_05_01 | 0x1c01 512x256 | DXT5 512x256 (linear) | 52.11 | credits: different staff lists (Vita lists the US localization team); NOT drop-in — keep JP or make custom |
| XUI_staff_staff_11_02 | 0x1c01 512x512 | DXT5 512x512 (linear) | 42.16 | credits: different staff lists (Vita lists the US localization team); NOT drop-in — keep JP or make custom |
| XUI_staff_staff_07_01 | 0x1c01 512x256 | DXT5 512x256 (linear) | 41.31 | credits: different staff lists (Vita lists the US localization team); NOT drop-in — keep JP or make custom |
| XUI_staff_staff_05_02 | 0x1c01 512x512 | DXT5 512x512 (linear) | 38.15 | credits: different staff lists (Vita lists the US localization team); NOT drop-in — keep JP or make custom |
| MenuBg_texture | 0x1c01 512x128 | DXT5 512x128 (linear) | 37.88 | no text; cosmetic difference only — skip |
| XUI_Loading_Skin_05_ef24_02_01 | 0x1c01 1024x64 | DXT5 1024x64 (linear) | 34.36 | DROP-IN (English text, same layout) |
| XUI_Loading_Skin_05_e551_02_01 | 0x1c01 512x64 | DXT5 512x64 (linear) | 34.15 | DROP-IN (English text, same layout) |
| XUI_staff_staff_04_02 | 0x1c01 512x256 | DXT5 512x256 (linear) | 32.26 | credits: different staff lists (Vita lists the US localization team); NOT drop-in — keep JP or make custom |
| XUI_ed_ed_07_04 | 0x1c01 256x32 | DXT5 256x32 (linear) | 29.37 | DROP-IN (English text, same layout) |
| System_texture | 0x2001 256x128 | DXT3 256x128 (linear) | 26.19 | BUILT: Vita Backup/Ride labels + Switch minus glyph, packed into System/resource.dxb |
| XUI_ed_ed_07_01 | 0x1c01 1024x128 | DXT5 1024x128 (linear) | 25.74 | DROP-IN (English text, same layout) |
| XUI_op_op_06_01 | 0x1c01 1024x512 | DXT5 1024x512 (linear) | 24.97 | DROP-IN (English text, same layout) |
| XUI_ed_ed_07_05 | 0x1c01 512x128 | DXT5 512x128 (linear) | 24.60 | DROP-IN (English text, same layout) |
| XUI_2p_win_2p_win_03 | 0x1c01 1024x128 | DXT5 1024x128 (linear) | 21.84 | DROP-IN (English text, same layout) |
| XUI_4p_win_4p_win_03 | 0x1b01 1024x128 | DXT3 1024x128 (linear) | 21.49 | DROP-IN (English text, same layout) |
| XUI_op_op_06_02 | 0x1c01 512x32 | DXT5 512x32 (linear) | 21.42 | DROP-IN (English text, same layout) |
| XUI_1p_win_1p_win_03 | 0x1c01 1024x128 | DXT5 1024x128 (linear) | 20.80 | DROP-IN (English text, same layout) |
| XUI_3p_win_3p_win_03 | 0x1b01 1024x128 | DXT3 1024x128 (linear) | 19.13 | DROP-IN (English text, same layout) |
| XUI_ed_ed_07_03 | 0x1c01 256x64 | DXT5 256x64 (linear) | 18.53 | DROP-IN (English text, same layout) |
| XUI_bg_10_bg_10_05 | 0x1c01 512x128 | DXT5 512x128 (linear) | 18.42 | no text; cosmetic difference only — skip |
| XUI_Loading_Skin_06_bb_02_01 | 0x1c01 512x64 | DXT5 512x64 (linear) | 18.15 | DROP-IN (English text, same layout) |
| XUI_Loading_Skin_06_sdl2_02_01 | 0x2001 512x64 | DXT5 512x64 (linear) | 14.07 | DROP-IN (English text, same layout) [BNTX retagged BC7 to DXT5] |
| XUI_loading_technical_loading_02_bg_02 | 0x1c01 1024x32 | DXT5 1024x32 (linear) | 13.74 | no text; cosmetic difference only — skip |
| XUI_loading_normal_loading_02_bg_02 | 0x1c01 1024x32 | DXT5 1024x32 (linear) | 13.74 | no text; cosmetic difference only — skip |
| XUI_2p_win_2p_win_04 | 0x1c01 1024x128 | DXT5 1024x128 (linear) | 13.46 | DROP-IN (English text, same layout) |
| XUI_loading_technical_loading_02_bg_06 | 0x2001 1024x512 | DXT3 1024x512 (linear) | 13.08 | BUILT: Vita English labels composited with authentic Switch glyphs |
| XUI_title_01_title_01_14_02 | 0x1c01 256x256 | DXT5 256x256 (linear) | 12.39 | title logo: Vita shows "EDF 2017 Portable"; NOT drop-in — keep JP logo or custom art |
| XUI_Loading_Skin_07_item_02_01 | 0x1c01 1024x512 | DXT5 1024x512 (linear) | 10.08 | DROP-IN (English text, same layout) |
| XUI_Loading_Skin_06_bb_02_02 | 0x2001 1024x512 | DXT3 1024x512 (linear) | 9.55 | BUILT: Vita English labels composited with authentic Switch glyphs |
| XUI_Loading_Skin_02_loading_bg_09 | 0x1c01 1024x512 | DXT5 1024x512 (linear) | 9.14 | DROP-IN (English text, same layout) |
| XUI_Loading_Skin_04_loading_bg_24 | 0x1c01 1024x512 | DXT5 1024x512 (linear) | 9.06 | DROP-IN (English text, same layout) |
| XUI_Loading_Skin_04_loading_bg_21 | 0x1c01 1024x512 | DXT5 1024x512 (linear) | 8.74 | DROP-IN (English text, same layout) |
| XUI_Loading_Skin_01_loading_bg_03 | 0x1c01 1024x512 | DXT5 1024x512 (linear) | 8.63 | DROP-IN (English text, same layout) |
| XUI_Loading_Skin_07_radar_02_04_05 | 0x1c01 512x128 | DXT5 512x128 (linear) | 8.08 | DROP-IN (English text, same layout) |
| XUI_Loading_Skin_02_loading_bg_12 | 0x1c01 1024x512 | DXT5 1024x512 (linear) | 7.86 | DROP-IN (English text, same layout) |
| XUI_Loading_Skin_03_loading_bg_15 | 0x1c01 1024x512 | DXT5 1024x512 (linear) | 6.97 | DROP-IN (English text, same layout) |
| XUI_Loading_Skin_01_loading_bg_02 | 0x1c01 1024x512 | DXT5 1024x512 (linear) | 6.71 | DROP-IN (English text, same layout) |
| XUI_Loading_Skin_05_ef24_02_02 | 0x2001 1024x512 | DXT3 1024x512 (linear) | 6.58 | BUILT: Vita English labels composited with authentic Switch glyphs |
| XUI_Loading_Skin_07_radar_02_04_01 | 0x1c01 512x128 | DXT5 512x128 (linear) | 6.35 | DROP-IN (English text, same layout) |
| XUI_Loading_Skin_07_radar_02_04_02 | 0x1c01 512x128 | DXT5 512x128 (linear) | 6.18 | DROP-IN (English text, same layout) |
| XUI_clear_01_clear_03_01 | 0x1c01 1024x256 | DXT5 1024x256 (linear) | 5.99 | no text; cosmetic difference only — skip |
| XUI_Loading_Skin_05_e551_02_02 | 0x2001 1024x512 | DXT3 1024x512 (linear) | 5.90 | BUILT: Vita English labels composited with authentic Switch glyphs |
| XUI_bg_10_bg_10_04 | 0x1c01 1024x64 | DXT5 1024x64 (linear) | 5.20 | no text; cosmetic difference only — skip |
| XUI_Loading_Skin_06_sdl2_02_02 | 0x2001 1024x512 | DXT3 1024x512 (linear) | 4.57 | BUILT: Vita English labels composited with authentic Switch glyphs |
| XUI_Loading_Skin_07_radar_02_04_03 | 0x1c01 512x128 | DXT5 512x128 (linear) | 4.22 | DROP-IN (English text, same layout) |
| XUI_3p_win_3p_win_04 | 0x1b01 1024x128 | DXT3 1024x128 (linear) | 3.23 | DROP-IN (English text, same layout) |
| XUI_Loading_Skin_03_loading_bg_18 | 0x1c01 1024x512 | DXT5 1024x512 (linear) | 2.98 | DROP-IN (English text, same layout) |
| XUI_Loading_Skin_07_radar_02_04_04 | 0x1c01 512x128 | DXT5 512x128 (linear) | 2.67 | DROP-IN (English text, same layout) |
| XUI_4p_win_4p_win_04 | 0x1b01 1024x128 | DXT3 1024x128 (linear) | 2.66 | DROP-IN (English text, same layout) |
| XUI_1p_win_1p_win_04 | 0x1c01 1024x128 | DXT5 1024x128 (linear) | 2.09 | DROP-IN (English text, same layout) |
| XUI_ed_ed_02 | 0x1c01 32x512 | DXT5 32x512 (linear) | 1.87 | DROP-IN (English text, same layout) |
| XUI_Loading_Skin_07_item_02_02 | 0x1c01 256x512 | DXT5 256x512 (linear) | 1.44 | DROP-IN (English text, same layout; this atlas slice contains no platform-specific glyph) |
| XUI_Loading_Skin_07_radar_02_01 | 0x1c01 1024x512 | DXT5 1024x512 (linear) | 0.69 | DROP-IN (English text, same layout) |
