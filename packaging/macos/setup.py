from pathlib import Path

from setuptools import setup

APP = [str(Path(__file__).resolve().parent.parent.parent / "src" / "app.py")]
OPTIONS = {
    "argv_emulation": False,
    "plist": {
        "CFBundleName": "Photo to PDF",
        "CFBundleDisplayName": "Photo to PDF",
        "CFBundleIdentifier": "com.nikitakrotenko.phototopdf",
        "CFBundleShortVersionString": "1.0.0",
    },
    "packages": ["PIL"],
}

setup(
    app=APP,
    name="Photo to PDF",
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
