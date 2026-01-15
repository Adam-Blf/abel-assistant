#!/usr/bin/env python3
"""
Script de build pour A.B.E.L Launcher (Rust/Tauri)
Usage: python build.py
"""

import subprocess
import sys
import shutil
from pathlib import Path


def main():
    root = Path(__file__).parent
    tauri_dir = root / "launcher-tauri" / "src-tauri"

    print("=" * 50)
    print("  A.B.E.L Launcher - Rust/Tauri Build")
    print("=" * 50)

    # 1. Verifier Rust
    print("\n[1/3] Verification de Rust...")
    try:
        result = subprocess.run(["rustc", "--version"], capture_output=True, text=True)
        print(f"  {result.stdout.strip()}")
    except FileNotFoundError:
        print("  [ERREUR] Rust non installe!")
        print("  Installez Rust: https://rustup.rs")
        sys.exit(1)

    # 2. Compiler
    print("\n[2/3] Compilation (mode release)...")
    result = subprocess.run(
        ["cargo", "build", "--release"],
        cwd=tauri_dir
    )

    if result.returncode != 0:
        print("\n[ERREUR] La compilation a echoue!")
        sys.exit(1)

    # 3. Copier l'executable
    print("\n[3/3] Finalisation...")
    src_exe = tauri_dir / "target" / "release" / "abel-launcher.exe"
    dist_dir = root / "dist"
    dist_dir.mkdir(exist_ok=True)
    dst_exe = dist_dir / "ABEL_Launcher.exe"

    if src_exe.exists():
        shutil.copy2(src_exe, dst_exe)
        size_mb = dst_exe.stat().st_size / (1024 * 1024)
        print(f"  Executable: {dst_exe}")
        print(f"  Taille: {size_mb:.1f} MB")
        print("\n" + "=" * 50)
        print("  BUILD REUSSI!")
        print("=" * 50)
    else:
        print("\n[ERREUR] Executable non trouve!")
        sys.exit(1)


if __name__ == "__main__":
    main()
