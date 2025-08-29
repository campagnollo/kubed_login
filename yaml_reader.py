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
