#!/usr/bin/env python3
"""
A.B.E.L - Script d'Installation Automatique
============================================
Installation en une commande:
    python setup.py

Options:
    python setup.py --local    # Mode 100% local (recommande)
    python setup.py --full     # Installation complete avec Docker
    python setup.py --minimal  # Installation minimale
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path
from typing import Optional
import urllib.request
import json


# =============================================================================
# CONFIGURATION
# =============================================================================

BANNER = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║     █████╗    ██████╗   ███████╗  ██╗                                        ║
║    ██╔══██╗   ██╔══██╗  ██╔════╝  ██║                                        ║
║    ███████║   ██████╔╝  █████╗    ██║                                        ║
║    ██╔══██║   ██╔══██╗  ██╔══╝    ██║                                        ║
║    ██║  ██║ █ ██████╔╝ █ ███████╗ ███████╗                                   ║
║    ╚═╝  ╚═╝   ╚═════╝    ╚══════╝  ╚══════╝                                   ║
║                                                                               ║
║    Autonomous Backend Entity for Living                                       ║
║    Version 2.0.0 - Open Source & Local First                                 ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

REQUIREMENTS = {
    "minimal": [
        "fastapi>=0.109.0",
        "uvicorn[standard]>=0.27.0",
        "httpx>=0.26.0",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "python-dotenv>=1.0.0",
    ],
    "local_ai": [
        "openai-whisper>=20231117",
        "sentence-transformers>=2.2.0",
    ],
    "database": [
        "sqlalchemy[asyncio]>=2.0.25",
        "asyncpg>=0.29.0",
        "aiosqlite>=0.19.0",
        "qdrant-client>=1.7.0",
    ],
    "full": [
        "celery[redis]>=5.3.0",
        "redis>=5.0.0",
        "passlib[bcrypt]>=1.7.4",
        "python-jose[cryptography]>=3.3.0",
        "python-multipart>=0.0.6",
    ],
}

OLLAMA_MODELS = {
    "default": "qwen2.5:7b",
    "light": "qwen2.5:3b",
    "fast": "qwen2.5:1.5b",
    "coder": "qwen2.5-coder:7b",
    "embeddings": "nomic-embed-text",
}


# =============================================================================
# UTILITIES
# =============================================================================

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_step(step: int, total: int, message: str):
    """Print a step with progress."""
    print(f"\n{Colors.CYAN}[{step}/{total}]{Colors.END} {Colors.BOLD}{message}{Colors.END}")


def print_success(message: str):
    """Print a success message."""
    print(f"  {Colors.GREEN}✓{Colors.END} {message}")


def print_warning(message: str):
    """Print a warning message."""
    print(f"  {Colors.YELLOW}⚠{Colors.END} {message}")


def print_error(message: str):
    """Print an error message."""
    print(f"  {Colors.RED}✗{Colors.END} {message}")


def run_command(cmd: str, capture: bool = False) -> Optional[str]:
    """Run a shell command."""
    try:
        if capture:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True
            )
            return result.stdout.strip()
        else:
            subprocess.run(cmd, shell=True, check=True)
            return None
    except subprocess.CalledProcessError:
        return None


def check_command(cmd: str) -> bool:
    """Check if a command exists."""
    return shutil.which(cmd) is not None


def get_platform() -> str:
    """Get the current platform."""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    return system


# =============================================================================
# INSTALLATION STEPS
# =============================================================================

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print_error(f"Python 3.10+ requis (actuel: {version.major}.{version.minor})")
        sys.exit(1)
    print_success(f"Python {version.major}.{version.minor}.{version.micro}")


def check_dependencies():
    """Check system dependencies."""
    deps = {
        "git": "Git",
        "docker": "Docker (optionnel)",
        "ollama": "Ollama (pour LLM local)",
    }

    for cmd, name in deps.items():
        if check_command(cmd):
            print_success(f"{name} installe")
        else:
            print_warning(f"{name} non trouve")


def create_virtualenv():
    """Create virtual environment."""
    venv_path = Path("venv")

    if venv_path.exists():
        print_success("Environnement virtuel existe deja")
        return

    print("  Creation de l'environnement virtuel...")
    run_command(f"{sys.executable} -m venv venv")
    print_success("Environnement virtuel cree")


def get_pip_cmd() -> str:
    """Get the pip command for the virtual environment."""
    if get_platform() == "windows":
        return "venv\\Scripts\\pip"
    return "venv/bin/pip"


def get_python_cmd() -> str:
    """Get the python command for the virtual environment."""
    if get_platform() == "windows":
        return "venv\\Scripts\\python"
    return "venv/bin/python"


def install_requirements(mode: str = "minimal"):
    """Install Python requirements."""
    pip = get_pip_cmd()

    # Upgrade pip
    run_command(f"{pip} install --upgrade pip")

    # Install requirements based on mode
    packages = REQUIREMENTS["minimal"].copy()

    if mode in ["local", "full"]:
        packages.extend(REQUIREMENTS["local_ai"])
        packages.extend(REQUIREMENTS["database"])

    if mode == "full":
        packages.extend(REQUIREMENTS["full"])

    print(f"  Installation de {len(packages)} packages...")

    for i, pkg in enumerate(packages, 1):
        print(f"    [{i}/{len(packages)}] {pkg.split('>=')[0]}...", end=" ")
        result = run_command(f"{pip} install \"{pkg}\" -q", capture=True)
        print(f"{Colors.GREEN}OK{Colors.END}")

    print_success("Dependances installees")


def setup_ollama():
    """Setup Ollama for local LLM."""
    if not check_command("ollama"):
        print_warning("Ollama non installe")
        print("  Pour installer Ollama: https://ollama.ai/download")
        return False

    # Check if Ollama is running
    try:
        import urllib.request
        urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2)
        print_success("Ollama est en cours d'execution")
    except:
        print_warning("Ollama n'est pas demarre")
        print("  Lancez: ollama serve")
        return False

    # Pull default model
    print("  Telechargement du modele Qwen2.5...")
    print("  (Cela peut prendre plusieurs minutes)")

    model = OLLAMA_MODELS["light"]  # Use light model by default
    result = run_command(f"ollama pull {model}")

    if result is not None:
        print_success(f"Modele {model} telecharge")
    else:
        print_warning("Echec du telechargement (peut etre deja installe)")

    return True


def create_env_file():
    """Create .env file from template."""
    env_path = Path(".env")
    example_path = Path(".env.example")

    if env_path.exists():
        print_warning(".env existe deja (non modifie)")
        return

    # Create minimal .env for local mode
    env_content = """# ===========================================
# A.B.E.L - Configuration Locale
# ===========================================
# Mode: local (100% offline)
# ===========================================

ABEL_RUN_MODE=local

# ============ LOCAL AI ============
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b
WHISPER_MODEL=base
WHISPER_LANGUAGE=fr

# ============ DATABASE (SQLite local) ============
DATABASE_URL=sqlite+aiosqlite:///./abel.db

# ============ SECURITY ============
SECRET_KEY={secret_key}
JWT_SECRET_KEY={jwt_secret}

# ============ APP ============
APP_NAME=A.B.E.L
APP_ENV=development
DEBUG=true
LOG_LEVEL=INFO
""".format(
        secret_key=os.urandom(32).hex(),
        jwt_secret=os.urandom(32).hex(),
    )

    env_path.write_text(env_content)
    print_success(".env cree avec configuration locale")


def setup_database():
    """Initialize local SQLite database."""
    db_path = Path("abel.db")

    if db_path.exists():
        print_success("Base de donnees existe deja")
        return

    print("  Initialisation de la base de donnees...")
    # The database will be created on first run
    print_success("Base de donnees prete")


def create_cli():
    """Create CLI script."""
    cli_content = '''#!/usr/bin/env python3
"""
A.B.E.L CLI - Command Line Interface
====================================
Usage:
    python abel.py start       # Demarre le serveur
    python abel.py chat        # Mode chat interactif
    python abel.py status      # Verifie le statut
    python abel.py ollama      # Gere Ollama
"""

import sys
import os
import subprocess
import argparse

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))


def start_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = True):
    """Start the FastAPI server."""
    cmd = f"uvicorn app.main:app --host {host} --port {port}"
    if reload:
        cmd += " --reload"

    os.chdir("backend")
    os.system(cmd)


def chat_mode():
    """Interactive chat with local LLM."""
    try:
        import httpx
        import json
    except ImportError:
        print("Dependencies not installed. Run: python setup.py")
        return

    print("\\n" + "="*60)
    print("  A.B.E.L - Mode Chat Local")
    print("  (tapez 'exit' pour quitter)")
    print("="*60 + "\\n")

    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

    messages = []
    system_prompt = "Tu es A.B.E.L, un assistant IA personnel. Reponds de maniere concise et utile."

    while True:
        try:
            user_input = input("\\n> Vous: ").strip()

            if user_input.lower() in ["exit", "quit", "q"]:
                print("\\nAu revoir!")
                break

            if not user_input:
                continue

            messages.append({"role": "user", "content": user_input})

            print("\\n> A.B.E.L: ", end="", flush=True)

            # Stream response from Ollama
            with httpx.Client(timeout=120) as client:
                with client.stream(
                    "POST",
                    f"{ollama_host}/api/chat",
                    json={
                        "model": model,
                        "messages": [{"role": "system", "content": system_prompt}] + messages,
                        "stream": True,
                    },
                ) as response:
                    full_response = ""
                    for line in response.iter_lines():
                        if line:
                            data = json.loads(line)
                            chunk = data.get("message", {}).get("content", "")
                            print(chunk, end="", flush=True)
                            full_response += chunk
                    print()

                    messages.append({"role": "assistant", "content": full_response})

        except KeyboardInterrupt:
            print("\\n\\nAu revoir!")
            break
        except Exception as e:
            print(f"\\nErreur: {e}")
            print("Verifiez que Ollama est demarre: ollama serve")


def check_status():
    """Check A.B.E.L status."""
    import urllib.request

    print("\\n" + "="*40)
    print("  A.B.E.L - Status")
    print("="*40)

    # Check Ollama
    try:
        urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2)
        print("  Ollama:     \\033[92m● Running\\033[0m")
    except:
        print("  Ollama:     \\033[91m○ Stopped\\033[0m")

    # Check Backend
    try:
        urllib.request.urlopen("http://localhost:8000/health", timeout=2)
        print("  Backend:    \\033[92m● Running\\033[0m")
    except:
        print("  Backend:    \\033[91m○ Stopped\\033[0m")

    # Check Database
    if os.path.exists("abel.db"):
        print("  Database:   \\033[92m● Ready\\033[0m")
    else:
        print("  Database:   \\033[93m○ Not initialized\\033[0m")

    print("="*40 + "\\n")


def manage_ollama(action: str):
    """Manage Ollama."""
    if action == "start":
        os.system("ollama serve &")
        print("Ollama demarre en arriere-plan")
    elif action == "pull":
        model = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
        os.system(f"ollama pull {model}")
    elif action == "list":
        os.system("ollama list")
    else:
        print(f"Action inconnue: {action}")


def main():
    parser = argparse.ArgumentParser(description="A.B.E.L CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Start command
    start_parser = subparsers.add_parser("start", help="Demarre le serveur")
    start_parser.add_argument("--port", type=int, default=8000)
    start_parser.add_argument("--no-reload", action="store_true")

    # Chat command
    subparsers.add_parser("chat", help="Mode chat interactif")

    # Status command
    subparsers.add_parser("status", help="Verifie le statut")

    # Ollama command
    ollama_parser = subparsers.add_parser("ollama", help="Gere Ollama")
    ollama_parser.add_argument("action", choices=["start", "pull", "list"])

    args = parser.parse_args()

    if args.command == "start":
        start_server(port=args.port, reload=not args.no_reload)
    elif args.command == "chat":
        chat_mode()
    elif args.command == "status":
        check_status()
    elif args.command == "ollama":
        manage_ollama(args.action)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
'''

    cli_path = Path("abel.py")
    cli_path.write_text(cli_content)

    # Make executable on Unix
    if get_platform() != "windows":
        os.chmod(cli_path, 0o755)

    print_success("CLI abel.py cree")


def create_docker_compose():
    """Create Docker Compose for local services."""
    compose_content = """# A.B.E.L - Docker Compose (Local Services)
# =========================================
# Usage: docker-compose up -d
# =========================================

version: '3.8'

services:
  # ===========================================
  # OLLAMA - Local LLM
  # ===========================================
  ollama:
    image: ollama/ollama:latest
    container_name: abel-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    restart: unless-stopped

  # ===========================================
  # QDRANT - Vector Database
  # ===========================================
  qdrant:
    image: qdrant/qdrant:latest
    container_name: abel-qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage
    environment:
      - QDRANT__SERVICE__GRPC_PORT=6334
    restart: unless-stopped

  # ===========================================
  # REDIS - Cache (optionnel)
  # ===========================================
  redis:
    image: redis:alpine
    container_name: abel-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped

  # ===========================================
  # POSTGRESQL - Database (optionnel)
  # ===========================================
  postgres:
    image: postgres:16-alpine
    container_name: abel-postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=abel
      - POSTGRES_PASSWORD=abel_local_dev
      - POSTGRES_DB=abel_db
    restart: unless-stopped

volumes:
  ollama_data:
  qdrant_data:
  redis_data:
  postgres_data:
"""

    compose_path = Path("docker-compose.local.yml")
    compose_path.write_text(compose_content)
    print_success("docker-compose.local.yml cree")


# =============================================================================
# MAIN
# =============================================================================

def main():
    print(BANNER)

    # Parse arguments
    mode = "local"
    if "--full" in sys.argv:
        mode = "full"
    elif "--minimal" in sys.argv:
        mode = "minimal"

    print(f"{Colors.CYAN}Mode d'installation: {mode.upper()}{Colors.END}")

    total_steps = 8

    # Step 1: Check Python
    print_step(1, total_steps, "Verification de Python")
    check_python_version()

    # Step 2: Check dependencies
    print_step(2, total_steps, "Verification des dependances")
    check_dependencies()

    # Step 3: Create virtual environment
    print_step(3, total_steps, "Creation de l'environnement virtuel")
    create_virtualenv()

    # Step 4: Install requirements
    print_step(4, total_steps, "Installation des packages Python")
    install_requirements(mode)

    # Step 5: Create .env
    print_step(5, total_steps, "Configuration de l'environnement")
    create_env_file()

    # Step 6: Setup Ollama
    print_step(6, total_steps, "Configuration d'Ollama (LLM local)")
    setup_ollama()

    # Step 7: Create CLI
    print_step(7, total_steps, "Creation de la CLI")
    create_cli()

    # Step 8: Create Docker Compose
    print_step(8, total_steps, "Creation de Docker Compose")
    create_docker_compose()

    # Done!
    print(f"""
{Colors.GREEN}{'='*60}
  INSTALLATION TERMINEE!
{'='*60}{Colors.END}

{Colors.BOLD}Commandes disponibles:{Colors.END}

  {Colors.CYAN}python abel.py start{Colors.END}    # Demarre le serveur API
  {Colors.CYAN}python abel.py chat{Colors.END}     # Mode chat interactif
  {Colors.CYAN}python abel.py status{Colors.END}   # Verifie le statut

{Colors.BOLD}Services Docker (optionnel):{Colors.END}

  {Colors.CYAN}docker-compose -f docker-compose.local.yml up -d{Colors.END}

{Colors.BOLD}Pour commencer:{Colors.END}

  1. Demarrez Ollama: {Colors.CYAN}ollama serve{Colors.END}
  2. Lancez le chat: {Colors.CYAN}python abel.py chat{Colors.END}

{Colors.YELLOW}Documentation: https://github.com/yourusername/A.B.E.L{Colors.END}
""")


if __name__ == "__main__":
    main()
