"""
Tests packaging integrity, artifact security scanning, and VS Code extension compatibility shims.
"""
import glob
import importlib.util
import os
import tarfile
import zipfile
import pytest


class TestPackagingAndSecurity:
    def test_wheel_contents_and_forbidden_files(self):
        wheels = glob.glob("dist/*.whl")
        assert len(wheels) > 0, "No built wheel found in dist/"
        wheel_path = wheels[0]

        with zipfile.ZipFile(wheel_path, "r") as z:
            names = z.namelist()

            # Ensure entrypoint and package metadata exist
            assert any("carboniq/__init__.py" in n for n in names)
            assert any("carboniq/cli/carboniq_cli.py" in n for n in names)
            assert any("entry_points.txt" in n for n in names)

            # Security: ensure NO forbidden files are packaged
            for name in names:
                lower = name.lower()
                assert ".env" not in lower, f"Security violation: env file in wheel: {name}"
                assert "measurements/" not in lower, f"Leakage: measurements folder in wheel: {name}"
                assert "backend/" not in lower, f"Leakage: backend folder in wheel: {name}"
                assert "frontend/" not in lower, f"Leakage: frontend folder in wheel: {name}"
                assert "vscode-extension/" not in lower, f"Leakage: vscode-extension in wheel: {name}"

                content = z.read(name).decode("utf-8", errors="ignore")
                assert "BEGIN RSA PRIVATE" not in content, f"Secret leakage in {name}"
                assert "BEGIN OPENSSH PRIVATE" not in content, f"Secret leakage in {name}"
                assert "AKIA" not in content, f"AWS key pattern detected in {name}"

    def test_sdist_contents(self):
        sdists = glob.glob("dist/*.tar.gz")
        assert len(sdists) > 0, "No built sdist found in dist/"
        sdist_path = sdists[0]

        with tarfile.open(sdist_path, "r:gz") as t:
            names = t.getnames()
            assert any("pyproject.toml" in n for n in names)
            assert any("carboniq/__init__.py" in n for n in names)
            for name in names:
                lower = name.lower()
                assert ".env" not in lower


class TestVSCodeExtensionCompatibility:
    @classmethod
    def setup_class(cls):
        """Ensure the checked-out source repository root is in sys.path specifically for repository-level shim compatibility verification."""
        import sys
        from pathlib import Path
        repo_root = str(Path(__file__).resolve().parent.parent)
        if repo_root not in sys.path:
            sys.path.insert(0, repo_root)

    def test_cli_shims_exist(self):
        """Verifies that the old cli.* import paths exist as shims in the source repo for backward compatibility."""
        import cli
        import cli.config_manager
        import cli.carboniq_cli
        assert hasattr(cli.config_manager, "get_config")
        assert hasattr(cli.carboniq_cli, "cli")

    def test_shim_cli_matches_package_cli(self):
        import cli.carboniq_cli as old_cli
        import carboniq.cli.carboniq_cli as pkg_cli
        assert old_cli.cli.name == pkg_cli.cli.name
        assert set(old_cli.cli.commands.keys()) == set(pkg_cli.cli.commands.keys())
