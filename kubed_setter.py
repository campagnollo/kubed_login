import os, sys, subprocess, yaml
from pathlib import Path
from dotenv import set_key, load_dotenv, find_dotenv
import pyperclip
import platform

# tests/test_smoke.py
def test_smoke():
    assert True


def main(cluster_name:str):

    env_path = find_dotenv(".env", usecwd=True)
    if not env_path:
        print("ERROR: .env not found", file=sys.stderr); sys.exit(1)
    load_dotenv(env_path, override=False)
    token = os.getenv("VAULT_TOKEN")
    if not token:
        print("ERROR: VAULT_TOKEN not set in .env", file=sys.stderr); sys.exit(1)
    clusters_path = Path(__file__).resolve().parent / "clusters-trunc.yaml"
    with open(clusters_path, "r", encoding="utf-8") as f:
        clusters = yaml.safe_load(f) or {}
    if cluster_name not in clusters:
        print(f"ERROR: cluster '{cluster_name}' not found.")
        sys.exit(1)
    c = clusters[cluster_name]
    env = os.environ.copy()
    env.update({
        "DOMAIN":          c["domain"],
        "CNC_DOMAIN":      c["CNC_DOMAIN"],
        "CNC":             c["CNC"],
        "VAULT_ADDR":      c["VAULT_ADDR"],
        "VAULT_NAMESPACE": c["VAULT_NAMESPACE"],
        "VAULT_TOKEN":     token,
    })
    paths = [env.get("PATH", "")]
    if platform.system() == "Darwin":
        paths = ["/usr/local/bin", "/opt/homebrew/bin"] + paths
    elif platform.system() == "Windows":
        paths = [
                    r"C:\Program Files\Git\bin",
                    r"C:\Windows\System32",
                ] + paths
    env["PATH"] = os.pathsep.join(paths)
    workdir = Path.home() / "k8s"
    if not workdir.exists():
        print(f"ERROR: missing directory {workdir}", file=sys.stderr); sys.exit(1)
    os.chdir(workdir)
    sign_on = Path.home()/"k8s/"/c["SIGN_ON"]
    if platform.system() == "Darwin":
        subprocess.run(["/bin/zsh", "-lic", sign_on], check=True, env=env)
    elif platform.system() == "Windows":
        subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", sign_on], check=True,
                       env=env)
    else:
        print("OS not identified. Exiting.")
        exit()

#
def vault_load():
    s = platform.system()
    if s == "Darwin":
        out = subprocess.check_output(["pbpaste", "-Prefer", "txt"])
    elif s == "Windows":
        out = subprocess.check_output(
            ["powershell", "-NoProfile", "-Command",
             "[Console]::OutputEncoding=[Text.UTF8Encoding]::UTF8; Get-Clipboard"],
            text=True
        ).rstrip("\r\n")
    else:
        print("OS not identified. Exiting.")
        exit()
    vault_var = out.decode("utf-8").rstrip("\r\n")
    if "hvs.CAE" not in vault_var:
        print("Vault token key not in clipboard. Exiting")
        sys.exit(1)
    dotenv_path = Path(".env")
    dotenv_path.touch()
    set_key(str(dotenv_path), "VAULT_TOKEN", vault_var, quote_mode="always")
    pyperclip.copy("")
    print("Vault token key uploaded")


if __name__ == "__main__":
    try:
        if sys.argv[1] == "vault":
            vault_load()
        else:
            main(sys.argv[1])
    except IndexError:
        print("Cluster name or vault required as a argument")
        exit()

