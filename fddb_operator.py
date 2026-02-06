import kopf
import kubernetes
from kubernetes import client, config
import yaml
import subprocess
import logging

logger = logging.getLogger(__name__)


def get_helm_values(spec):
    values = {
        'image': {
            'repository': 'ghcr.io/benni1390/fddb-exporter',
            'tag': spec.get('image', {}).get('tag', '0.0.1'),
            'pullPolicy': 'IfNotPresent'
        },
        'env': {
            'EXPORTER_PORT': '8000',
            'SCRAPE_INTERVAL': spec.get('scrapeInterval', '300'),
            'FDDB_DATE_OFFSET': '0'
        },
        'secrets': {
            'credentialsSecretName': spec.get('credentialsSecretName', 'fddb-credentials')
        },
        'serviceMonitor': {
            'enabled': spec.get('serviceMonitor', {}).get('enabled', True),
            'interval': spec.get('serviceMonitor', {}).get('interval', '30s')
        },
        'prometheusRule': {
            'enabled': spec.get('prometheusRule', {}).get('enabled', True)
        }
    }

    if 'resources' in spec:
        values['resources'] = spec['resources']

    return values


def install_helm_chart(name, namespace, spec):
    chart_version = spec.get('helmChart', {}).get('version', '0.0.14')
    values = get_helm_values(spec)

    values_file = f'/tmp/{name}-values.yaml'
    with open(values_file, 'w') as f:
        yaml.dump(values, f)

    cmd = [
        'helm', 'upgrade', '--install',
        name,
        'benni1390/fddb-exporter',
        '--version', chart_version,
        '--namespace', namespace,
        '--create-namespace',
        '--values', values_file
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise kopf.PermanentError(f"Helm install failed: {result.stderr}")

    return result.stdout


def uninstall_helm_chart(name, namespace):
    cmd = ['helm', 'uninstall', name, '--namespace', namespace]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.warning(f"Helm uninstall warning: {result.stderr}")
    return result.stdout


@kopf.on.create('fddb.benni1390.github.io', 'v1alpha1', 'fddbexporters')
def create_fn(spec, name, namespace, logger, **kwargs):
    logger.info(f"Creating FddbExporter {name} in namespace {namespace}")

    output = install_helm_chart(name, namespace, spec)
    logger.info(f"Helm output: {output}")

    return {'helm-release': name, 'status': 'created'}


@kopf.on.update('fddb.benni1390.github.io', 'v1alpha1', 'fddbexporters')
def update_fn(spec, name, namespace, logger, **kwargs):
    logger.info(f"Updating FddbExporter {name} in namespace {namespace}")

    output = install_helm_chart(name, namespace, spec)
    logger.info(f"Helm output: {output}")

    return {'helm-release': name, 'status': 'updated'}


@kopf.on.delete('fddb.benni1390.github.io', 'v1alpha1', 'fddbexporters')
def delete_fn(spec, name, namespace, logger, **kwargs):
    logger.info(f"Deleting FddbExporter {name} in namespace {namespace}")

    output = uninstall_helm_chart(name, namespace)
    logger.info(f"Helm output: {output}")

    return {'helm-release': name, 'status': 'deleted'}
