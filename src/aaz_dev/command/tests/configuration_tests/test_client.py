from unittest import TestCase
from command.model.configuration._client import *
from datetime import datetime
from utils.plane import PlaneEnum
from utils.client import CloudEnum
from utils import exceptions


class ClientConfigurationTest(TestCase):

    def test_client_config(self):
        cfg = CMDClientConfig({
            "plane": PlaneEnum.Data("Microsoft.Insights"),
            "auth": {
                "aad": {
                    "scopes": [
                        "https://metrics.monitor.azure.com/.default"
                    ]
                }
            }
        })
        cfg.endpoints = CMDClientEndpointsByTemplate({
            "type": "templates",
            "templates": [{
                "cloud": CloudEnum.AzureCloud,
                "template": "https://global.metrics.monitor.azure.com/"
            }, {
                "cloud": CloudEnum.AzureChinaCloud,
                "template": "https://global.metrics.monitor.azure.com/"
            }]
        })
        cfg.version = datetime.utcnow()
        cfg.endpoints.prepare()
        cfg.generate_args()
        cfg.reformat()

        cfg.validate()
        cfg.to_native()
        cfg.to_primitive()

        self.assertEqual(cfg.arg_group, None)
        self.assertEqual(cfg.endpoints.params, None)

    def test_client_config_with_params(self):
        cfg = CMDClientConfig({
            "plane": PlaneEnum.Data("Microsoft.Insights"),
            "auth": {
                "aad": {
                    "scopes": [
                        "https://metrics.monitor.azure.com/.default"
                    ]
                }
            }
        })
        cfg.endpoints = CMDClientEndpointsByTemplate({
            "type": "templates",
            "templates": [{
                "cloud": CloudEnum.AzureCloud,
                "template": "https://{region}.{zone}.metrics.monitor.azure.com/"
            }, {
                "cloud": CloudEnum.AzureChinaCloud,
                "template": "https://{region}.{zone}.metrics.monitor.azure.com/"
            }]
        })
        cfg.version = datetime.utcnow()
        cfg.endpoints.prepare()
        cfg.generate_args()
        cfg.reformat()

        cfg.validate()
        cfg.to_native()
        cfg.to_primitive()

        self.assertEqual(cfg.endpoints.templates[0].template, 'https://{region}.{zone}.metrics.monitor.azure.com')
        self.assertEqual(len(cfg.arg_group.args), 2)
        self.assertEqual(cfg.arg_group.args[0].var, '$Client.Endpoint.region')
        self.assertEqual(cfg.arg_group.args[0].options, ['region'])
        self.assertEqual(cfg.arg_group.args[0].required, True)
        self.assertEqual(cfg.arg_group.args[1].var, '$Client.Endpoint.zone')
        self.assertEqual(cfg.arg_group.args[1].options, ['zone'])
        self.assertEqual(cfg.arg_group.args[1].required, True)

    def test_client_config_reformat(self):
        cfg = CMDClientConfig({
            "plane": PlaneEnum.Data("Microsoft.Insights"),
            "auth": {
                "aad": {
                    "scopes": [
                        "https://metrics.monitor.azure.com/.default"
                    ]
                }
            }
        })
        cfg.endpoints = CMDClientEndpointsByTemplate({
            "type": "templates",
            "templates": [{
                "cloud": CloudEnum.AzureCloud,
                "template": "https://{region}.metrics.monitor.azure.com/part1/part2"
            }]
        })
        cfg.version = datetime.utcnow()
        cfg.endpoints.prepare()
        cfg.generate_args()
        with self.assertRaises(exceptions.VerificationError):
            cfg.reformat()

    def test_client_config_generate_args(self):
        cfg = CMDClientConfig({
            "plane": PlaneEnum.Data("Microsoft.Insights"),
            "auth": {
                "aad": {
                    "scopes": [
                        "https://metrics.monitor.azure.com/.default"
                    ]
                }
            }
        })
        cfg.endpoints = CMDClientEndpointsByTemplate({
            "type": "templates",
            "templates": [{
                "cloud": CloudEnum.AzureCloud,
                "template": "https://{region}.metrics.monitor.azure.com"
            }, {
                "cloud": CloudEnum.AzureChinaCloud,
                "template": "https://{region}.{zone}.metrics.monitor.azure.com"
            }
            ]
        })
        cfg.version = datetime.utcnow()
        cfg.endpoints.prepare()
        cfg.generate_args()

        with self.assertRaises(exceptions.VerificationError):
            cfg.reformat()
