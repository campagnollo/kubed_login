"""Transform a source cluster list into a trimmed, per-cluster mapping.

Reads a source YAML file (default: ``clusters-1756205308442.yaml``) containing a
top-level ``clusters`` list, and writes a new YAML file
(default: ``clusters-trunc.yaml``) keyed by cluster **name**. Each output entry
includes the cluster’s ``domain``, a fixed set of common fields, and a
prebuilt sign-on command.

Input schema (source YAML):
    clusters:
      - name: "<cluster-name>"
        domain: "<fqdn or domain>"
        # ...other fields are ignored

Output schema (written YAML):
    <cluster-name>:
      domain: "<domain from source>"
      CNC_DOMAIN: "prod.infra.webex.com"
      CNC: "mccprod"
      VAULT_ADDR: "https://keeper.cisco.com"
      VAULT_NAMESPACE: "meetpaas/mccprod"
      SIGN_ON: "kubectl-wbx3 login <cluster-name> --role k8s-admin"

Behavior:
- If the source file is missing, prints an error to stderr and exits with code 1.
- If the source YAML is invalid, prints the parse error to stderr and exits with code 1.
- If an item in ``clusters`` lacks ``name`` or ``domain``, prints a warning and skips it.
- Only ``name`` and ``domain`` are consumed from the source; the rest are ignored.
- Common fields are hard-coded in the script (see ``common``).

Dependencies:
- PyYAML (``pip install pyyaml``)

Usage:
    python this_script.py
    # or import and call main()

Notes:
- Update ``src``/``dst`` at the top of ``main()`` to change filenames.
- The output preserves insertion order (``sort_keys=False`` in ``yaml.safe_dump``).
"""

import yaml
import sys
from pathlib import Path

def main():
    src = 'clusters-1756205308442.yaml'
    dst = 'clusters-trunc.yaml'

    try:
        cfg = yaml.safe_load(Path(src).read_text(encoding='utf-8')) or {}
    except FileNotFoundError:
        print(f"ERROR: file not found: {src}", file=sys.stderr);
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"ERROR: invalid YAML in {src}: {e}", file=sys.stderr);
        sys.exit(1)

    common = {
        'CNC_DOMAIN': 'prod.infra.webex.com',
        'CNC': 'mccprod',
        'VAULT_ADDR': 'https://keeper.cisco.com',
        'VAULT_NAMESPACE': 'meetpaas/mccprod'
        }

    new_clusters = {}
    for i, cluster in enumerate(cfg.get('clusters', [])):
        name = cluster.get('name')
        dom = cluster.get('domain')
        if not name or not dom:
            print(f"WARNING: item #{i} missing name/domain; skipping", file=sys.stderr)
            continue

        body = {
            'domain': dom,  # from source
            **common,  # your hard-coded fields
            'SIGN_ON': f'kubectl-wbx3 login {name} --role k8s-admin'
        }
        new_clusters[name] = body

    with open('clusters-trunc.yaml', 'w', encoding='utf-8') as f:
        yaml.safe_dump(new_clusters, f, sort_keys=False)


if __name__ == '__main__':
    main()
