#!/usr/bin/env python3
"""
A.B.E.L - Security Validation Script
=====================================
Verifie que toutes les corrections de securite sont appliquees.
"""

import sys
import os
from pathlib import Path
import re

# Couleurs pour le terminal
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def check_error_exposure(file_path: Path) -> list[str]:
    """Verifie qu'aucune erreur n'est exposee avec str(e)."""
    issues = []
    content = file_path.read_text(encoding="utf-8")

    # Chercher les patterns dangereux
    patterns = [
        (r'detail=str\(e\)', "Exposition de detail d'erreur avec str(e)"),
        (r'detail=f".*\{e\}"', "Exposition de detail d'erreur dans f-string"),
        (r'detail=.*\+.*str\(.*\)', "Concatenation avec str() dans detail"),
    ]

    for pattern, description in patterns:
        matches = re.finditer(pattern, content, re.MULTILINE)
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            issues.append(f"  Line {line_num}: {description}")

    return issues


def check_docs_in_production(main_file: Path) -> list[str]:
    """Verifie que les docs sont desactivees en production."""
    issues = []
    content = main_file.read_text(encoding="utf-8")

    # Verifier que docs_url, redoc_url, openapi_url sont conditionnels
    required_patterns = [
        r'docs_url="/docs" if not settings\.is_production else None',
        r'redoc_url="/redoc" if not settings\.is_production else None',
        r'openapi_url="/openapi\.json" if not settings\.is_production else None',
    ]

    for pattern in required_patterns:
        if not re.search(pattern, content):
            issues.append(f"  Pattern manquant: {pattern}")

    return issues


def check_security_headers(main_file: Path) -> list[str]:
    """Verifie que les security headers sont ajoutes."""
    issues = []
    content = main_file.read_text(encoding="utf-8")

    # Verifier l'import
    if "from app.core.security import add_security_headers" not in content:
        issues.append("  Import manquant: from app.core.security import add_security_headers")

    # Verifier l'ajout du middleware
    if 'app.middleware("http")(add_security_headers)' not in content:
        issues.append("  Middleware manquant: app.middleware('http')(add_security_headers)")

    return issues


def check_config_secrets(config_file: Path) -> list[str]:
    """Verifie que les secrets n'ont pas de valeurs par defaut."""
    issues = []
    content = config_file.read_text(encoding="utf-8")

    # Patterns dangereux
    dangerous_patterns = [
        (r'secret_key.*=.*Field\(default="[^"]+', "secret_key a une valeur par defaut non-vide"),
        (r'database_url.*=.*Field\(.*default="postgresql://', "database_url a une valeur par defaut"),
    ]

    for pattern, description in dangerous_patterns:
        if re.search(pattern, content):
            issues.append(f"  {description}")

    # Verifier la presence des validateurs
    if "@field_validator" not in content:
        issues.append("  Aucun field_validator trouve")

    if "validate_secret_key" not in content:
        issues.append("  Validateur validate_secret_key manquant")

    if "validate_database_url" not in content:
        issues.append("  Validateur validate_database_url manquant")

    return issues


def check_deps_file(deps_file: Path) -> list[str]:
    """Verifie que le fichier deps.py existe et contient les dependances."""
    issues = []

    if not deps_file.exists():
        issues.append("  Fichier deps.py manquant")
        return issues

    content = deps_file.read_text(encoding="utf-8")

    required_functions = ["get_optional_user", "get_required_user"]
    for func in required_functions:
        if f"async def {func}" not in content:
            issues.append(f"  Fonction {func} manquante")

    return issues


def main():
    """Execute toutes les verifications."""
    print(f"\n{YELLOW}=== A.B.E.L Security Validation ==={RESET}\n")

    # Chemins des fichiers
    backend_dir = Path(__file__).parent.parent
    api_dir = backend_dir / "app" / "api"
    core_dir = backend_dir / "app" / "core"

    all_passed = True

    # 1. Verifier l'exposition des erreurs dans tous les fichiers API
    print(f"{YELLOW}1. Verification de l'exposition des erreurs...{RESET}")
    api_files = [
        api_dir / "chat.py",
        api_dir / "voice.py",
        api_dir / "memory.py",
        api_dir / "health.py",
    ]

    for api_file in api_files:
        if api_file.exists():
            issues = check_error_exposure(api_file)
            if issues:
                all_passed = False
                print(f"{RED}[FAIL] {api_file.name}{RESET}")
                for issue in issues:
                    print(f"{RED}{issue}{RESET}")
            else:
                print(f"{GREEN}[PASS] {api_file.name}{RESET}")
        else:
            print(f"{YELLOW}[SKIP] {api_file.name} - fichier non trouve{RESET}")

    # 2. Verifier la desactivation des docs en production
    print(f"\n{YELLOW}2. Verification de la desactivation des docs en production...{RESET}")
    main_file = backend_dir / "app" / "main.py"
    if main_file.exists():
        issues = check_docs_in_production(main_file)
        if issues:
            all_passed = False
            print(f"{RED}[FAIL] main.py{RESET}")
            for issue in issues:
                print(f"{RED}{issue}{RESET}")
        else:
            print(f"{GREEN}[PASS] main.py{RESET}")
    else:
        print(f"{RED}[FAIL] main.py - fichier non trouve{RESET}")
        all_passed = False

    # 3. Verifier les security headers
    print(f"\n{YELLOW}3. Verification des security headers...{RESET}")
    if main_file.exists():
        issues = check_security_headers(main_file)
        if issues:
            all_passed = False
            print(f"{RED}[FAIL] main.py{RESET}")
            for issue in issues:
                print(f"{RED}{issue}{RESET}")
        else:
            print(f"{GREEN}[PASS] main.py{RESET}")

    # 4. Verifier les secrets dans config.py
    print(f"\n{YELLOW}4. Verification des secrets dans config.py...{RESET}")
    config_file = core_dir / "config.py"
    if config_file.exists():
        issues = check_config_secrets(config_file)
        if issues:
            all_passed = False
            print(f"{RED}[FAIL] config.py{RESET}")
            for issue in issues:
                print(f"{RED}{issue}{RESET}")
        else:
            print(f"{GREEN}[PASS] config.py{RESET}")
    else:
        print(f"{RED}[FAIL] config.py - fichier non trouve{RESET}")
        all_passed = False

    # 5. Verifier le fichier deps.py
    print(f"\n{YELLOW}5. Verification du fichier deps.py...{RESET}")
    deps_file = api_dir / "deps.py"
    issues = check_deps_file(deps_file)
    if issues:
        all_passed = False
        print(f"{RED}[FAIL] deps.py{RESET}")
        for issue in issues:
            print(f"{RED}{issue}{RESET}")
    else:
        print(f"{GREEN}[PASS] deps.py{RESET}")

    # Resultat final
    print(f"\n{YELLOW}=== Resultat Final ==={RESET}")
    if all_passed:
        print(f"{GREEN}[OK] Tous les tests de securite ont reussi!{RESET}\n")
        return 0
    else:
        print(f"{RED}[FAIL] Certains tests de securite ont echoue.{RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
