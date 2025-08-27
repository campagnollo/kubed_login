import yaml

def main():
    with open('clusters-1756205308442.yaml', 'r') as f:
        cfg = yaml.safe_load(f)

    common = {
        'CNC_DOMAIN': 'prod.infra.webex.com',
        'CNC': 'mccprod',
        'VAULT_ADDR': 'https://keeper.cisco.com',
        'VAULT_NAMESPACE': 'meetpaas/mccprod',
        'VAULT_TOKEN': 'a12345'
    }

    new_clusters = []
    for cluster in cfg.get('clusters', []):
        cluster_name = cluster.get('name')
        cluster_dom = cluster.get('domain')
        new_clusters.append({
            'name': cluster_name,
            'domain': cluster_dom,
            **common,
            'SIGN_ON': 'wbx3 login ' + cluster_name + ' --role k8s-admin'
        })



    with open('clusters-trunc.yaml', 'w') as f:
        yaml.safe_dump({'clusters': new_clusters}, f, sort_keys=False)

if __name__ == '__main__':
    main()
