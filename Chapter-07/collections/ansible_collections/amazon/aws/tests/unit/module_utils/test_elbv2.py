#
# (c) 2021 Red Hat Inc.
#
# This file is part of Ansible
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.amazon.aws.plugins.module_utils import elbv2
from ansible_collections.amazon.aws.tests.unit.compat import unittest
from ansible_collections.amazon.aws.tests.unit.compat.mock import MagicMock

one_action = [
    {
        "ForwardConfig": {
            "TargetGroupStickinessConfig": {"Enabled": False},
            "TargetGroups": [
                {
                    "TargetGroupArn": "arn:aws:elasticloadbalancing:us-east-1:966509639900:targetgroup/my-tg-58045486/5b231e04f663ae21",
                    "Weight": 1,
                }
            ],
        },
        "TargetGroupArn": "arn:aws:elasticloadbalancing:us-east-1:966509639900:targetgroup/my-tg-58045486/5b231e04f663ae21",
        "Type": "forward",
    }
]


def test__prune_ForwardConfig():
    expectation = {
        "TargetGroupArn": "arn:aws:elasticloadbalancing:us-east-1:966509639900:targetgroup/my-tg-58045486/5b231e04f663ae21",
        "Type": "forward",
    }
    assert elbv2._prune_ForwardConfig(one_action[0]) == expectation


def _prune_secret():
    assert elbv2._prune_secret(one_action[0]) == one_action[0]


def _sort_actions_one_entry():
    assert elbv2._sort_actions(one_action) == one_action


class ElBV2UtilsTestSuite(unittest.TestCase):

    def setUp(self):
        self.connection = MagicMock(name="connection")
        self.module = MagicMock(name="module")

        self.module.params = dict()

        self.conn_paginator = MagicMock(name="connection.paginator")
        self.paginate = MagicMock(name="paginator.paginate")

        self.connection.get_paginator.return_value = self.conn_paginator
        self.conn_paginator.paginate.return_value = self.paginate

        self.loadbalancer = {
            "Type": "application",
            "Scheme": "internet-facing",
            "IpAddressType": "ipv4",
            "VpcId": "vpc-3ac0fb5f",
            "AvailabilityZones": [
                {
                    "ZoneName": "us-west-2a",
                    "SubnetId": "subnet-8360a9e7"
                },
                {
                    "ZoneName": "us-west-2b",
                    "SubnetId": "subnet-b7d581c0"
                }
            ],
            "CreatedTime": "2016-03-25T21:26:12.920Z",
            "CanonicalHostedZoneId": "Z2P70J7EXAMPLE",
            "DNSName": "my-load-balancer-424835706.us-west-2.elb.amazonaws.com",
            "SecurityGroups": [
                "sg-5943793c"
            ],
            "LoadBalancerName": "my-load-balancer",
            "State": {
                "Code": "active"
            },
            "LoadBalancerArn": "arn:aws:elasticloadbalancing:us-west-2:123456789012:loadbalancer/app/my-load-balancer/50dc6c495c0c9188"
        }
        self.paginate.build_full_result.return_value = {
            'LoadBalancers': [self.loadbalancer]
        }

        self.connection.describe_load_balancer_attributes.return_value = {
            "Attributes": [
                {
                    "Value": "false",
                    "Key": "access_logs.s3.enabled"
                },
                {
                    "Value": "",
                    "Key": "access_logs.s3.bucket"
                },
                {
                    "Value": "",
                    "Key": "access_logs.s3.prefix"
                },
                {
                    "Value": "60",
                    "Key": "idle_timeout.timeout_seconds"
                },
                {
                    "Value": "false",
                    "Key": "deletion_protection.enabled"
                },
                {
                    "Value": "true",
                    "Key": "routing.http2.enabled"
                }
            ]
        }
        self.connection.describe_tags.return_value = {
            "TagDescriptions": [
                {
                    "ResourceArn": "arn:aws:elasticloadbalancing:us-west-2:123456789012:loadbalancer/app/my-load-balancer/50dc6c495c0c9188",
                    "Tags": [
                        {
                            "Value": "ansible",
                            "Key": "project"
                        },
                        {
                            "Value": "RedHat",
                            "Key": "company"
                        }
                    ]
                }
            ]
        }
        self.elbv2obj = elbv2.ElasticLoadBalancerV2(self.connection, self.module)

    # Test the simplest case - Read the ip address type
    def test_get_elb_ip_address_type(self):
        # Run module
        return_value = self.elbv2obj.get_elb_ip_address_type()
        # check that no method was called and this has been retrieved from elb attributes
        self.connection.describe_load_balancer_attributes.assert_called_once()
        self.connection.get_paginator.assert_called_once()
        self.connection.describe_tags.assert_called_once()
        self.conn_paginator.paginate.assert_called_once()
        # assert we got the expected value
        self.assertEqual(return_value, 'ipv4')

    # Test modify_ip_address_type idempotency
    def test_modify_ip_address_type_idempotency(self):
        # Run module
        return_value = self.elbv2obj.modify_ip_address_type("ipv4")
        # check that no method was called and this has been retrieved from elb attributes
        self.connection.set_ip_address_type.assert_not_called()
        # assert we got the expected value
        self.assertEqual(self.elbv2obj.changed, False)

    # Test modify_ip_address_type
    def test_modify_ip_address_type_update(self):
        # Run module
        return_value = self.elbv2obj.modify_ip_address_type("dualstack")
        # check that no method was called and this has been retrieved from elb attributes
        self.connection.set_ip_address_type.assert_called_once()
        # assert we got the expected value
        self.assertEqual(self.elbv2obj.changed, True)
