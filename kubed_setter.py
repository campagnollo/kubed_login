import os, sys, subprocess, yaml
from pathlib import Path
from dotenv import set_key, load_dotenv, find_dotenv
import pyperclip
import platform

def vault_load():
    s = platform.system()
    if s == "Darwin":
        return subprocess.check_output(["pbpaste"]).decode("utf-8")
    if s == "Windows":
        return subprocess.check_output(
            ["powershell", "-NoProfile", "-Command",
             "[Console]::OutputEncoding=[Text.UTF8Encoding]::UTF8; Get-Clipboard"]
        ).decode("utf-8")
    # Linux/BSD
    for cmd in (["wl-paste", "-n"], ["xclip", "-selection", "clipboard", "-o"], ["xsel", "-b", "-o"]):
        try:
            return subprocess.check_output(cmd).decode("utf-8")
        except Exception:
            pass
    raise RuntimeError("No clipboard utility found.")


def _run_script_cross_platform(script_path: Path, env: dict, cwd: Path):
    """Run .ps1/.bat/.cmd/.sh (or an executable) on Windows/macOS/Linux."""
    script_path = script_path.resolve()
    ext = script_path.suffix.lower()
    system = platform.system()

    if system == "Windows":
        if ext == ".ps1":
            pwsh = shutil.which("pwsh") or shutil.which("powershell")
            if not pwsh:
                raise RuntimeError("PowerShell not found (need pwsh or powershell).")
            return subprocess.run(
                [pwsh, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script_path)],
                check=True, env=env, cwd=str(cwd)
            )
        if ext in (".bat", ".cmd"):
            # shell=True so cmd.exe runs the batch script
            return subprocess.run(str(script_path), check=True, env=env, cwd=str(cwd), shell=True)
        if ext == ".sh":
            # Prefer Git Bash; fallback to WSL if available
            if shutil.which("bash"):
                return subprocess.run(["bash", str(script_path)], check=True, env=env, cwd=str(cwd))
            if shutil.which("wsl"):
                return subprocess.run(["wsl", "bash", str(script_path)], check=True, env=env, cwd=str(cwd))
            raise RuntimeError("No bash available to run .sh on Windows (install Git for Windows or WSL).")
        # Try running directly (e.g., .exe, .py with shebang)
        return subprocess.run([str(script_path)], check=True, env=env, cwd=str(cwd), shell=ext=="")

    # macOS/Linux
    if ext == ".sh":
        sh = shutil.which("bash") or shutil.which("zsh") or shutil.which("sh")
        return subprocess.run([sh, str(script_path)], check=True, env=env, cwd=str(cwd))
    if ext == ".ps1":
        pwsh = shutil.which("pwsh") or shutil.which("powershell")
        if not pwsh:
            raise RuntimeError("PowerShell not found to run .ps1")
        return subprocess.run([pwsh, "-NoProfile", "-File", str(script_path)], check=True, env=env, cwd=str(cwd))

    return subprocess.run([str(script_path)], check=True, env=env, cwd=str(cwd))


def main(cluster_name: str):
    # 1) Load .env (cross-platform)
    env_path = find_dotenv(".env", usecwd=True)
    if not env_path:
        print("ERROR: .env not found", file=sys.stderr); sys.exit(1)
    load_dotenv(env_path, override=False)

    token = os.getenv("VAULT_TOKEN")
    if not token:
        print("ERROR: VAULT_TOKEN not set in .env", file=sys.stderr); sys.exit(1)

    # 2) Read clusters mapping
    clusters_path = Path(__file__).resolve().parent / "clusters-trunc.yaml"
    with open(clusters_path, "r", encoding="utf-8") as f:
        clusters = yaml.safe_load(f) or {}
    if cluster_name not in clusters:
        print(f"ERROR: cluster '{cluster_name}' not found.", file=sys.stderr); sys.exit(1)

    c = clusters[cluster_name]

    # 3) Build env safely and prepend platform-appropriate PATH entries that actually exist
    env = os.environ.copy()
    env.update({
        "DOMAIN":          c["domain"],
        "CNC_DOMAIN":      c["CNC_DOMAIN"],
        "CNC":             c["CNC"],
        "VAULT_ADDR":      c["VAULT_ADDR"],
        "VAULT_NAMESPACE": c["VAULT_NAMESPACE"],
        "VAULT_TOKEN":     token,
    })

    prepend_paths = []
    if platform.system() == "Windows":
        prepend_paths += [
            r"C:\Program Files\Git\bin",           # Git Bash (if installed)
            r"C:\Windows\System32",
        ]
    else:
        prepend_paths += [
            "/usr/local/bin",    # Intel Homebrew (macOS)
            "/opt/homebrew/bin", # Apple Silicon Homebrew (macOS)
            "/usr/bin",          # common on Linux
        ]
    prepend_paths = [p for p in prepend_paths if Path(p).exists()]
    env["PATH"] = os.pathsep.join(prepend_paths + [env.get("PATH", "")])

    # 4) Use a portable workdir and script path
    workdir = Path.home() / "k8s"
    if not workdir.exists():
        print(f"ERROR: missing directory {workdir}", file=sys.stderr); sys.exit(1)

    # SIGN_ON is now resolved relative to workdir (no hard-coded /Users/... path)
    sign_on = (workdir / c["SIGN_ON"]).resolve()
    if not sign_on.exists():
        print(f"ERROR: sign-on script not found: {sign_on}", file=sys.stderr); sys.exit(1)

    # 5) Run the script cross-platform without changing global CWD
    _run_script_cross_platform(sign_on, env=env, cwd=workdir)




if __name__ == "__main__":
    try:
        if sys.argv[1] == "vault":
            vault_load()
        else:
            main(sys.argv[1])
    except IndexError:
        print("Cluster name or vault required as a argument")
        exit()

