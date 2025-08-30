# kubed_setter.py

A small, focused helper script to **prepare your local environment for accessing a Kubernetes cluster** and **manage your Vault token** using a simple one‑word command. It reads a cluster definition from a YAML file and **emits shell `export` lines** so your current shell picks up consistent environment variables for tools like `kubectl`.

> This README is generated from the parts of the script that are visible: it expects a `.env` file, a `clusters-trunc.yaml` file, and it supports two entry modes: a **cluster name** or the keyword **`vault`**. If your private copy has extra options, add them in the “Advanced / Customize” section below.

---

## Why use this?
- **One command to switch clusters.** Keeps your shell environment consistent for kubectl and related tools.
- **Safe secret handling.** Emits `export` lines so values land in your shell without echoing secrets verbatim in logs; avoid committing `.env` files with secrets.
- **YAML‑driven.** All cluster‑specific values live in a single `clusters-trunc.yaml` file you can version independently (excluding secrets).

---

## How it works (at a glance)
- On startup, the script may read a **`.env`** from the current working directory (e.g., to pick up `VAULT_TOKEN`). If absent, you can still run the cluster export step; errors will mention what’s missing.
- It **loads** the `.env` and looks for **`VAULT_TOKEN`**. If absent, it stops with: `ERROR: VAULT_TOKEN not set in .env` (unless you first run the `vault` mode).
- It **opens `clusters-trunc.yaml`** from the same directory as the script and reads cluster definitions.
- **Invocation modes:**
  - `python kubed_setter.py vault` → runs the script’s vault loader (e.g., to capture a Vault token into `.env`).
  - `python kubed_setter.py <cluster-name>` → reads that cluster’s values from the YAML and **outputs shell `export` statements** that you should evaluate to populate your current shell environment.
- If no argument is provided, it prints: `Cluster name or vault required as a argument`.

> Note: The exact keys written to `.env` depend on your YAML structure. Common values include `KUBECONFIG`, `KUBE_CLUSTER`, `NAMESPACE`, `VAULT_ADDR`, or other cluster‑specific environment variables your workflow expects.

---

## Requirements

- **Python** 3.8+ (tested with recent 3.x)
- **Packages**
  - `pyyaml`
  - `python-dotenv`

Install packages (recommended: use a virtualenv):
```bash
pip install pyyaml python-dotenv
```

---

## Files & Layout

```
your-project/
├─ .env                   # optional; can pre-store `VAULT_TOKEN` or other defaults you source manually
├─ clusters-trunc.yaml    # required; per-cluster settings (non-secret)
├─ kubed_setter.py        # the script
```

- **`.env`** is **optional**. You may preload values (like `VAULT_TOKEN`) or skip it entirely and rely on the script’s exports.
- **`clusters-trunc.yaml`** must be next to `kubed_setter.py` (the script resolves its own directory and opens that file).

---

## Example `clusters-trunc.yaml`

This is an example structure. Adapt the keys to what your tooling needs (they’ll be written into `.env`).

```yaml
# clusters-trunc.yaml
wdfwgen-p-4:
  KUBECONFIG: "/Users/you/k8s/configs/wdfwgen-p-4.kubeconfig"
  KUBE_CLUSTER: "wdfwgen-p-4"
  NAMESPACE: "default"
  VAULT_ADDR: "https://vault.example.com"

wdfwmw-dc-1:
  KUBECONFIG: "/Users/you/k8s/configs/wdfwmw-dc-1.kubeconfig"
  KUBE_CLUSTER: "wdfwmw-dc-1"
  NAMESPACE: "platform"
  VAULT_ADDR: "https://vault.example.com"
```

---

## Example `.env`

Start minimal; the script will add/update keys. Keep this file **out of git**.

```dotenv
# .env
VAULT_TOKEN=               # leave blank first; set via `python kubed_setter.py vault`
# Values below are managed by kubed_setter.py
KUBECONFIG=
KUBE_CLUSTER=
NAMESPACE=
VAULT_ADDR=
```

Add `.env` to your `.gitignore`:
```gitignore
.env
```

---

## Usage

From the project directory, **evaluate** the exports so they affect your current shell:

```bash
# 1) Export your Vault token into the current shell
eval "$(python kubed_setter.py vault)"

# 2) Switch to a cluster (exports that cluster's env vars)
eval "$(python kubed_setter.py wdfwgen-p-4)"
```

**Recommended shell function (zsh/bash):**

```bash
# Add to ~/.zshrc or ~/.bashrc
kubed() {
  eval "$(python3 /absolute/path/to/kubed_setter.py "$@")"
}

# Then just run:
kubed vault
kubed wdfwgen-p-4
```


**Nice quality-of-life alias (macOS/Linux zsh/bash):**
```bash
alias kubed='python3 /absolute/path/to/kubed_setter.py'
kubed vault
kubed wdfwgen-p-4
```

> If your script integrates with `kubectl`, you can now run `kubectl ...` using the environment from `.env` (e.g., `KUBECONFIG`). Consider sourcing `.env` in your shell or having your other tools load it automatically.

---

## Troubleshooting

- **Exports don’t “stick”**  
  Ensure you’re using `eval "$(python kubed_setter.py <name>)"` **or** the `kubed()` function wrapper so variables land in your current shell.

- **`ERROR: VAULT_TOKEN not set`**  
  Run the vault step first and evaluate its output:
  ```bash
  eval "$(python kubed_setter.py vault)"
  ```

- **`FileNotFoundError: clusters-trunc.yaml`**  
  Ensure `clusters-trunc.yaml` lives **next to** `kubed_setter.py` and is readable. The script resolves:
  ```text
  Path(__file__).resolve().parent / "clusters-trunc.yaml"
  ```

- **Cluster not found**  
  Make sure the name you pass on the command line exactly matches a top‑level key in `clusters-trunc.yaml`.

- **Environment not updating**  
  The script **prints** `export KEY=VALUE` lines. Make sure you evaluate them in your current shell (see Usage).

---

## Security Notes

- Secrets should live in `.env`, which should **never** be committed to version control.
- `clusters-trunc.yaml` should contain **non‑secret** per‑cluster values (paths, names, endpoints). Put tokens/credentials in `.env` only.
- Consider file permissions on `.env` (e.g., `chmod 600 .env`).

---

## Advanced / Customize

- **YAML schema**: Add any keys your tooling expects. The script will write them to `.env`.
- **Multiple `.env` files**: If you keep per‑project or per‑cluster `.env` files, you can adapt the script or use shell wrappers to point to the right one.
- **Shell integration**: You can add a small wrapper that runs the script then `export`/`source` values from `.env`.

---

## License

Add a license of your choice (MIT, Apache‑2.0, etc.) if you plan to publish this project.

---

## Acknowledgements

- [`python-dotenv`](https://github.com/theskumar/python-dotenv)
- [`PyYAML`](https://pyyaml.org/)

