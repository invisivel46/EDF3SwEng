import argparse
import hashlib
import io
import os
import struct
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools/scripts"))

import edf3_patch_builder as builder
import sgo
import sgsl
import statmerge
import tex_bntx
import xmlbin
from build_controller_textures import centre_paste
from PIL import Image


class HashTests(unittest.TestCase):
    def test_sha1_file(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "sample.bin"
            path.write_bytes(b"EDF3" * 1000)
            self.assertEqual(builder.sha1_file(path), hashlib.sha1(path.read_bytes()).hexdigest())

    def test_verify_sha1_accepts_match(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "sample.bin"; path.write_bytes(b"known")
            expected = hashlib.sha1(b"known").hexdigest()
            self.assertEqual(builder.verify_sha1(path, expected, "test", lambda _x: None), expected)

    def test_verify_sha1_rejects_mismatch(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "sample.bin"; path.write_bytes(b"wrong")
            with self.assertRaisesRegex(builder.BuildError, "wrong region/version"):
                builder.verify_sha1(path, "0" * 40, "test", lambda _x: None)

    def test_reference_hashes_are_sha1(self):
        self.assertGreaterEqual(len(builder.KNOWN_SHA1), 6)
        for digest in builder.KNOWN_SHA1.values():
            self.assertRegex(digest, r"^[0-9a-f]{40}$")

    def test_container_sha1_match_is_true(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "game.nsp"; path.write_bytes(b"container")
            expected = hashlib.sha1(b"container").hexdigest()
            messages = []
            self.assertTrue(builder.check_container_sha1(path, expected, "NSP", messages.append))
            self.assertIn("Exact reference container match", "\n".join(messages))

    def test_container_sha1_mismatch_is_advisory(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "repacked.nsp"; path.write_bytes(b"same content, other packing")
            messages = []
            self.assertFalse(builder.check_container_sha1(path, "0" * 40, "NSP", messages.append))
            self.assertIn("extracted content will be verified", "\n".join(messages))


class SafetyTests(unittest.TestCase):
    def test_windows_subprocesses_are_hidden(self):
        if os.name == "nt":
            self.assertEqual(builder.NO_WINDOW, builder.subprocess.CREATE_NO_WINDOW)

    def test_run_captures_child_without_console(self):
        messages = []
        builder.run([sys.executable, "-c", "print('child output')"], messages.append)
        self.assertIn("child output", messages)

    def test_redact_title_key_argument(self):
        line = builder.redact("hactool --titlekey=00112233445566778899aabbccddeeff file.nca")
        self.assertNotIn("001122", line)
        self.assertIn("redacted", line)

    def test_redact_title_key_diagnostic(self):
        self.assertEqual(builder.redact("TitleKey: secret"), "[title key output redacted]")


class InputTests(unittest.TestCase):
    def test_sanitized_keys(self):
        with tempfile.TemporaryDirectory() as td:
            source = Path(td) / "prod.keys"
            output = Path(td) / "clean.keys"
            source.write_text("good = " + "AB" * 16 + "\ninvalid = xyz\ntoo_short = aa\n")
            builder.sanitized_keys(source, output)
            self.assertEqual(output.read_text(), "good = " + "ab" * 16 + "\n")

    def test_sanitized_keys_rejects_empty(self):
        with tempfile.TemporaryDirectory() as td:
            source = Path(td) / "prod.keys"; source.write_text("not a key")
            with self.assertRaises(builder.BuildError):
                builder.sanitized_keys(source, Path(td) / "out")

    def test_ticket_title_key(self):
        with tempfile.TemporaryDirectory() as td:
            ticket = Path(td) / "title.tik"
            ticket.write_bytes(bytes(0x180) + bytes.fromhex("00112233445566778899aabbccddeeff"))
            self.assertEqual(builder.ticket_title_key(Path(td)), "00112233445566778899aabbccddeeff")

    def test_ticket_title_key_absent(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertIsNone(builder.ticket_title_key(Path(td)))

    def test_ticket_title_key_rejects_short_ticket(self):
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "title.tik").write_bytes(b"short")
            with self.assertRaisesRegex(builder.BuildError, "too small"):
                builder.ticket_title_key(Path(td))

    def test_locate_decrypted_vita_root(self):
        with tempfile.TemporaryDirectory() as td:
            game = Path(td) / "nested/PCSE00209"
            (game / "US").mkdir(parents=True); (game / "US/data.psarc").write_bytes(b"PSAR")
            self.assertEqual(builder.locate_vita_root(Path(td)), game)

    def test_locate_nopndr_vita_root(self):
        with tempfile.TemporaryDirectory() as td:
            game = Path(td) / "app/PCSE00209"; game.mkdir(parents=True)
            self.assertEqual(builder.locate_vita_root(Path(td)), game)

    def test_locate_vita_root_rejects_ambiguous_archives(self):
        with tempfile.TemporaryDirectory() as td:
            for name in ("one", "two"):
                folder = Path(td) / name / "US"; folder.mkdir(parents=True)
                (folder / "data.psarc").write_bytes(b"PSAR")
            self.assertIsNone(builder.locate_vita_root(Path(td)))

    def test_safe_zip_extract(self):
        with tempfile.TemporaryDirectory() as td:
            archive = Path(td) / "vita.zip"
            with zipfile.ZipFile(archive, "w") as zf: zf.writestr("PCSE00209/US/data.psarc", b"PSAR")
            output = Path(td) / "out"; output.mkdir()
            builder.safe_extract_zip(archive, output)
            self.assertEqual((output / "PCSE00209/US/data.psarc").read_bytes(), b"PSAR")

    def test_safe_zip_rejects_traversal(self):
        with tempfile.TemporaryDirectory() as td:
            archive = Path(td) / "bad.zip"
            with zipfile.ZipFile(archive, "w") as zf: zf.writestr("../escape.bin", b"bad")
            output = Path(td) / "out"; output.mkdir()
            with self.assertRaisesRegex(builder.BuildError, "Unsafe path"):
                builder.safe_extract_zip(archive, output)


class FormatTests(unittest.TestCase):
    def test_sgsl_round_trip(self):
        source = (b"Sandlot-EDF3-" * 1000) + bytes(range(256))
        self.assertEqual(sgsl.decompress(sgsl.compress(source)), source)

    def test_sgo_keyed_round_trip(self):
        values = ["Earth Defense Force", 3, 1.25, ["A", "B"]]
        keys = ["title", "number", "scale", "items"]
        data = sgo.build_keyed(values, keys)
        parsed, _ = sgo.parse(data)
        self.assertEqual(parsed, values)
        self.assertEqual(sgo.parse_keys(data), keys)

    def test_xmlbin_round_trip(self):
        header = b"TEST"
        records = [(b"\x01\x00\x02\x03", "Hello"), (b"\x02\x00\x04\x05", "World")]
        got_header, got_records = xmlbin.read(xmlbin.write(header, records))
        self.assertEqual(got_header, header)
        self.assertEqual(got_records, records)

    def test_bntx_format_retag_and_swizzle(self):
        data = bytearray(0x300)
        data[0x20:0x24] = b"BRTI"
        struct.pack_into("<BBHHHHHIIIIIII", data, 0x30,
                         0, 2, 0, 0, 1, 1, 0, 0x2001, 0, 4, 4, 1, 1, 0)
        struct.pack_into("<I", data, 0x70, 512)
        struct.pack_into("<Q", data, 0x90, 0xC0)
        struct.pack_into("<Q", data, 0xC0, 0x100)
        blocks = bytes.fromhex("ff" * 16)
        encoded = tex_bntx.encode(bytes(data), blocks, "DXT5")
        self.assertEqual(tex_bntx._info(encoded)["fmt"], 0x1C01)
        self.assertEqual(tex_bntx.deswizzle(encoded), blocks)

    def test_controller_glyph_preserves_size(self):
        dst = Image.new("RGBA", (20, 20), (1, 2, 3, 255))
        src = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
        src.putpixel((4, 4), (255, 255, 255, 255))
        centre_paste(dst, src, (5, 5, 15, 15), (2, 2, 7, 7))
        self.assertEqual(dst.size, (20, 20))
        self.assertEqual(dst.getpixel((9, 9)), (255, 255, 255, 255))

    def test_statmerge_preserves_switch_numbers(self):
        log = []
        result = statmerge.merge("!Damage 50 / Range 100", "!Damage 45 / Range 90", log, "weapon")
        self.assertIn("50", result)
        self.assertIn("100", result)


class RepositoryIntegrationTests(unittest.TestCase):
    def test_install_instructions_contain_all_supported_targets(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            builder.write_install_instructions(root)
            text = (root / "INSTALL.txt").read_text(encoding="utf-8")
            self.assertIn(builder.TITLE_ID, text)
            self.assertIn("Atmosphere", text)
            self.assertIn("Ryujinx", text)
            self.assertIn("LayerFS", text)

    def test_cli_parser_accepts_complete_invocation(self):
        args = builder.parser().parse_args([
            "--cli", "--switch", "game.nsp", "--keys", "prod.keys",
            "--vita", "vita.zip", "--output", "out", "--overwrite",
        ])
        self.assertTrue(args.cli)
        self.assertTrue(args.overwrite)
        self.assertEqual(args.vita, "vita.zip")

    def test_translation_manifest_counts(self):
        import csv
        with open(ROOT / "work/audio/voice_review.csv", encoding="utf-8") as source:
            rows = list(csv.DictReader(source))
        spoken = [r for r in rows if r["verdict"] in ("confirmed", "low-confidence", "no-match")]
        self.assertEqual(len(spoken), 4807)

    def test_patch_inventory_when_built(self):
        romfs = ROOT / "patch/romfs"
        if not romfs.is_dir(): self.skipTest("patch has not been built")
        self.assertEqual(len(list(romfs.rglob("*.sgo"))), 413)
        self.assertEqual(len(list(romfs.rglob("*.bntx"))), 46)
        self.assertEqual(len(list((romfs / "Sound/stream").glob("*.bfstm"))), 4807)

    def test_all_built_audio_is_switch_endian(self):
        paths = list((ROOT / "patch/romfs/Sound/stream").glob("*.bfstm"))
        if not paths: self.skipTest("audio patch has not been built")
        for path in paths:
            with self.subTest(path=path.name):
                self.assertEqual(path.read_bytes()[:6], b"FSTM\xff\xfe")


if __name__ == "__main__":
    unittest.main()
