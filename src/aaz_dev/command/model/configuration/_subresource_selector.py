# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from schematics.models import Model

from ._fields import CMDVariantField
from ._selector_index import CMDSelectorIndexField


class CMDSubresourceSelector(Model):
    POLYMORPHIC_KEY = None
    DEFAULT_VARIANT = "$Subresource"

    # properties as tags
    var = CMDVariantField(required=True, default=DEFAULT_VARIANT)
    ref = CMDVariantField(required=True)

    class Options:
        serialize_when_none = False

    @classmethod
    def _claim_polymorphic(cls, data):
        if cls.POLYMORPHIC_KEY is None:
            return False

        if isinstance(data, dict):
            return cls.POLYMORPHIC_KEY in data
        elif isinstance(data, CMDSubresourceSelector):
            return hasattr(data, cls.POLYMORPHIC_KEY)
        return False

    def generate_args(self, ref_args):
        raise NotImplementedError()

    def reformat(self, **kwargs):
        raise NotImplementedError()


class CMDJsonSubresourceSelector(CMDSubresourceSelector):
    """
    : example 1
        <subresourceSelector var="$SubresourceSelector_1" ref="$Instance">
          <json type="object" name="parameters">
            <prop type="array<object>" name="properties.subnets">
              <identifier type="string" name="[Index]" arg="$parameters.properties.subnets[Index]" />
              <item type="object">
                <prop type="array<object>" name="properties.applicationGatewayIpConfigurations">
                  <identifier type="string" name="[].id" arg="$parameters.properties.subnets[].properties.applicationGatewayIpConfigurations[].id"/>
                  <identifier type="string" name="[].name" arg="$parameters.properties.subnets[].properties.applicationGatewayIpConfigurations[].name"/>
                  <item type="object">
                  </item>
                </prop>
              </item>
            </prop>
          </json>
        </subresourceSelector>

    : example 2
        <subresourceSelector var="$SubresourceSelector_2" ref="$Instance">
          <json type="object" name="parameters">
            <prop type="array<object>" name="properties.subnets">
              <identifier type="string" name="[].name" arg="$parameters.properties.subnets[].name" />
              <item type="object">
                <prop type="object" name="properties.applicationGatewayIpConfigurations">
                  <additionalProp>
                    <identifier type="string" name="{Key}" arg="$parameters.properties.subnets[].properties.applicationGatewayIpConfigurations{Key}"/>
                    <item type="object">
                    </item>
                  </additionalProp>
                </prop>
              </item>
            </prop>
          </json>
        </subresourceSelector>

    : example 3
        <subresourceSelector var="$SubresourceSelector_3" ref="$Instance">
          <json type="object" name="parameters">
            <prop type="array<object>" name="properties.subnets">
              <identifier type="string" name="[].name" arg="$parameters.properties.subnets[].name" />
              <item type="object">
                <discriminator property="type" value="AzureFunctionActivity">
                  <prop type="object" name="properties.applicationGatewayIpConfigurations">
                    <additionalProp>
                      <identifier type="string" name="{}.id" arg="$parameters.properties.subnets[].AzureFunctionActivity.properties.applicationGatewayIpConfigurations{}.id"/>
                      <identifier type="string" name="{}.name" arg="$parameters.properties.subnets[].AzureFunctionActivity.properties.applicationGatewayIpConfigurations{}.name"/>
                      <item type="object">
                      </item>
                    </additionalProp>
                  </prop>
                </discriminator>
              </item>
            </prop>
          </json>
        </subresourceSelector>
    """

    POLYMORPHIC_KEY = "json"

    # properties as nodes
    json = CMDSelectorIndexField(required=True)

    def generate_args(self, ref_args):
        return self.json.generate_args(ref_args, "$")

    def reformat(self, **kwargs):
        self.json.reformat(**kwargs)
