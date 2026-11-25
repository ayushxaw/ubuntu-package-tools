import io
import os
from pathlib import Path
import runpy
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
PYTHON = "/usr/bin/python3"


class IntegrationTests(unittest.TestCase):
    def test_setup_and_uninstall(self):
        with TemporaryDirectory(prefix="package installer ") as home:
            base = Path(home)
            data = base / "custom data"
            env = {**os.environ, "HOME": home, "XDG_DATA_HOME": str(data)}
            setup = [PYTHON, str(ROOT / "setup")]
            subprocess.run([*setup, "install"], env=env, check=True)
            desktop = data / "applications/ubuntu-package-installer-gdebi.desktop"
            subprocess.run(["desktop-file-validate", str(desktop)], check=True)
            self.assertIn(str(data / "ubuntu-package-installer/gdebi-wayland"), desktop.read_text())
            command = base / ".local/bin/ubuntu-package-download"
            subprocess.run([str(command), "--help"], env=env, check=True, capture_output=True)
            extension = data / "nautilus-python/extensions/ubuntu_package_installer.py"
            self.assertTrue(extension.is_file())

            appimage = base / "Example App.AppImage"
            payload = b"\x7fELF\x02\x01\x01\x00AI\x02sample"
            appimage.write_bytes(payload)
            installer = data / "ubuntu-package-installer/install-appimage"
            subprocess.run(
                [PYTHON, "-c", "import pathlib, runpy, sys; runpy.run_path(sys.argv[1])['install'](pathlib.Path(sys.argv[2]))", str(installer), str(appimage)],
                env=env, check=True,
            )
            installed, = (base / "Applications").glob("*/app.AppImage")
            launcher, = (data / "applications").glob("appimage-*.desktop")
            self.assertEqual(installed.read_bytes(), payload)
            self.assertTrue(os.access(installed, os.X_OK))
            subprocess.run(["desktop-file-validate", str(launcher)], check=True)

            subprocess.run([*setup, "uninstall"], env=env, check=True)
            self.assertFalse(extension.exists())
            self.assertFalse(desktop.exists())
            self.assertFalse(command.is_symlink())
            self.assertTrue(launcher.exists())
            self.assertTrue(installed.exists())

    def test_download_and_no_overwrite(self):
        download = runpy.run_path(str(ROOT / "src/download-package"))["download"]
        payload = b"!<arch>\nexample"
        response = io.BytesIO(payload)
        response.headers = {"Content-Length": str(len(payload))}
        opener = Mock()
        opener.open.return_value = response
        with TemporaryDirectory() as temp, patch.dict(download.__globals__, build_opener=Mock(return_value=opener)):
            directory = Path(temp)
            path = download("https://example.com/my%20package.deb", directory)
            self.assertEqual(path.name, "my package.deb")
            self.assertEqual(path.read_bytes(), payload)
            with self.assertRaises(FileExistsError):
                download("https://example.com/my%20package.deb", directory)

    def test_download_rejects_http_and_incomplete_payload(self):
        download = runpy.run_path(str(ROOT / "src/download-package"))["download"]
        response = io.BytesIO(b"!<arch>\nexample")
        response.headers = {"Content-Length": "100"}
        opener = Mock()
        opener.open.return_value = response
        with TemporaryDirectory() as temp, patch.dict(download.__globals__, build_opener=Mock(return_value=opener)):
            directory = Path(temp)
            with self.assertRaisesRegex(ValueError, "HTTPS"):
                download("http://example.com/package.deb", directory)
            with self.assertRaisesRegex(ValueError, "incomplete"):
                download("https://example.com/package.deb", directory)
            self.assertEqual(list(directory.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
