import os, sys, subprocess, yaml
from pathlib import Path
from dotenv import set_key, load_dotenv, find_dotenv


def main(cluster_name):
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
    env["PATH"] = os.pathsep.join([
        "/usr/local/bin",          # Intel Homebrew
        "/opt/homebrew/bin",       # Apple Silicon Homebrew
        env.get("PATH",""),
    ])
    workdir = Path.home() / "k8s"
    if not workdir.exists():
        print(f"ERROR: missing directory {workdir}", file=sys.stderr); sys.exit(1)
    os.chdir(workdir)
    sign_on = "/Users/ericmoo/k8s/"+c["SIGN_ON"]
    subprocess.run(["/bin/zsh", "-lic", sign_on], check=True, env=env)

#
def vault_load():
    out = subprocess.check_output(["pbpaste", "-Prefer", "txt"])
    vault_var = out.decode("utf-8").rstrip("\r\n")
    if "hvs.CAE" not in vault_var:
        print("Vault token key not in clipboard. Exiting")
        sys.exit(1)
    dotenv_path = Path(".env")
    dotenv_path.touch()
    set_key(str(dotenv_path), "VAULT_TOKEN", vault_var, quote_mode="always")
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

