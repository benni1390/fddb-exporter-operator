import pytest
from unittest.mock import patch, MagicMock
from fddb_operator import get_helm_values, install_helm_chart, uninstall_helm_chart


def test_get_helm_values_minimal():
    spec = {}
    values = get_helm_values(spec)

    assert values['image']['tag'] == '0.0.1'
    assert values['env']['SCRAPE_INTERVAL'] == '300'
    assert values['secrets']['credentialsSecretName'] == 'fddb-credentials'
    assert values['serviceMonitor']['enabled'] is True


def test_get_helm_values_custom():
    spec = {
        'image': {'tag': '0.0.2'},
        'scrapeInterval': '600',
        'credentialsSecretName': 'custom-secret',
        'serviceMonitor': {
            'enabled': False,
            'interval': '60s'
        },
        'resources': {
            'requests': {'cpu': '100m', 'memory': '128Mi'},
            'limits': {'cpu': '500m', 'memory': '256Mi'}
        }
    }
    values = get_helm_values(spec)

    assert values['image']['tag'] == '0.0.2'
    assert values['env']['SCRAPE_INTERVAL'] == '600'
    assert values['secrets']['credentialsSecretName'] == 'custom-secret'
    assert values['serviceMonitor']['enabled'] is False
    assert values['serviceMonitor']['interval'] == '60s'
    assert values['resources']['requests']['cpu'] == '100m'


@patch('fddb_operator.subprocess.run')
@patch('fddb_operator.yaml.dump')
@patch('builtins.open', create=True)
def test_install_helm_chart_success(mock_open, mock_yaml_dump, mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout='Success', stderr='')

    spec = {'helmChart': {'version': '0.0.14'}}
    result = install_helm_chart('test-release', 'test-namespace', spec)

    assert result == 'Success'
    mock_run.assert_called_once()
    call_args = mock_run.call_args[0][0]
    assert 'helm' in call_args
    assert 'upgrade' in call_args
    assert '--install' in call_args
    assert 'test-release' in call_args
    assert 'benni1390/fddb-exporter' in call_args


@patch('fddb_operator.subprocess.run')
@patch('fddb_operator.yaml.dump')
@patch('builtins.open', create=True)
def test_install_helm_chart_failure(mock_open, mock_yaml_dump, mock_run):
    mock_run.return_value = MagicMock(returncode=1, stdout='', stderr='Error')

    spec = {}
    with pytest.raises(Exception) as exc_info:
        install_helm_chart('test-release', 'test-namespace', spec)

    assert 'Helm install failed' in str(exc_info.value)


@patch('fddb_operator.subprocess.run')
def test_uninstall_helm_chart(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout='Uninstalled', stderr='')

    result = uninstall_helm_chart('test-release', 'test-namespace')

    assert result == 'Uninstalled'
    mock_run.assert_called_once()
    call_args = mock_run.call_args[0][0]
    assert 'helm' in call_args
    assert 'uninstall' in call_args
    assert 'test-release' in call_args
    assert 'test-namespace' in call_args
