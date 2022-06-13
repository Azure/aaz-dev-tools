# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# Code generated by aaz-dev-tools
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines

from azure.cli.core.aaz import *


@register_command(
    "sentinel automation-rule update",
)
class Update(AAZCommand):
    """Creates or updates the automation rule
    """

    _aaz_info = {
        "version": "2021-10-01",
        "resources": [
            ["mgmt-plane", "/subscriptions/{}/resourcegroups/{}/providers/microsoft.operationalinsights/workspaces/{}/providers/microsoft.securityinsights/automationrules/{}", "2021-10-01"],
        ]
    }

    AZ_SUPPORT_GENERIC_UPDATE = True

    def _handler(self, command_args):
        super()._handler(command_args)
        self._execute_operations()
        return self._output()

    _args_schema = None

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        if cls._args_schema is not None:
            return cls._args_schema
        cls._args_schema = super()._build_arguments_schema(*args, **kwargs)

        # define Arg Group ""

        _args_schema = cls._args_schema
        _args_schema.automation_rule_id = AAZStrArg(
            options=["--automation-rule-id", "--name", "-n"],
            help="Automation rule ID",
            required=True,
            id_part="child_name_1",
        )
        _args_schema.resource_group = AAZResourceGroupNameArg(
            required=True,
        )
        _args_schema.workspace_name = AAZStrArg(
            options=["--workspace-name"],
            help="The name of the workspace.",
            required=True,
            id_part="name",
        )

        # define Arg Group "AutomationRuleToUpsert"

        _args_schema = cls._args_schema
        _args_schema.etag = AAZStrArg(
            options=["--etag"],
            arg_group="AutomationRuleToUpsert",
            help="Etag of the azure resource",
        )
        _args_schema.actions = AAZListArg(
            options=["--actions"],
            singular_options=["--action"],
            arg_group="AutomationRuleToUpsert",
            help="The actions to execute when the automation rule is triggered",
        )
        _args_schema.display_name = AAZStrArg(
            options=["--display-name"],
            arg_group="AutomationRuleToUpsert",
            help="The display name of the automation rule",
        )
        _args_schema.order = AAZIntArg(
            options=["--order"],
            arg_group="AutomationRuleToUpsert",
            help="The order of execution of the automation rule",
        )
        _args_schema.triggering_logic = AAZObjectArg(
            options=["--triggering-logic"],
            arg_group="AutomationRuleToUpsert",
            help="Describes automation rule triggering logic",
        )

        actions = cls._args_schema.actions
        actions.Element = AAZObjectArg()

        _element = cls._args_schema.actions.Element
        _element.modify_properties = AAZObjectArg(
            options=["modify-properties"],
        )
        _element.run_playbook = AAZObjectArg(
            options=["run-playbook"],
        )
        _element.order = AAZIntArg(
            options=["order"],
        )

        modify_properties = cls._args_schema.actions.Element.modify_properties
        modify_properties.action_configuration = AAZObjectArg(
            options=["action-configuration"],
        )

        action_configuration = cls._args_schema.actions.Element.modify_properties.action_configuration
        action_configuration.classification = AAZStrArg(
            options=["classification"],
            help="The reason the incident was closed",
            enum={"BenignPositive": "BenignPositive", "FalsePositive": "FalsePositive", "TruePositive": "TruePositive", "Undetermined": "Undetermined"},
        )
        action_configuration.classification_comment = AAZStrArg(
            options=["classification-comment"],
            help="Describes the reason the incident was closed",
        )
        action_configuration.classification_reason = AAZStrArg(
            options=["classification-reason"],
            help="The classification reason the incident was closed with",
            enum={"InaccurateData": "InaccurateData", "IncorrectAlertLogic": "IncorrectAlertLogic", "SuspiciousActivity": "SuspiciousActivity", "SuspiciousButExpected": "SuspiciousButExpected"},
        )
        action_configuration.labels = AAZListArg(
            options=["labels"],
            singular_options=["label"],
            help="List of labels to add to the incident",
        )
        action_configuration.owner = AAZObjectArg(
            options=["owner"],
            help="Information on the user an incident is assigned to",
        )
        action_configuration.severity = AAZStrArg(
            options=["severity"],
            help="The severity of the incident",
            enum={"High": "High", "Informational": "Informational", "Low": "Low", "Medium": "Medium"},
        )
        action_configuration.status = AAZStrArg(
            options=["status"],
            help="The status of the incident",
            enum={"Active": "Active", "Closed": "Closed", "New": "New"},
        )

        labels = cls._args_schema.actions.Element.modify_properties.action_configuration.labels
        labels.Element = AAZObjectArg()

        _element = cls._args_schema.actions.Element.modify_properties.action_configuration.labels.Element
        _element.label_name = AAZStrArg(
            options=["label-name"],
            help="The name of the label",
        )

        owner = cls._args_schema.actions.Element.modify_properties.action_configuration.owner
        owner.assigned_to = AAZStrArg(
            options=["assigned-to"],
            help="The name of the user the incident is assigned to.",
        )
        owner.email = AAZStrArg(
            options=["email"],
            help="The email of the user the incident is assigned to.",
        )
        owner.object_id = AAZStrArg(
            options=["object-id"],
            help="The object id of the user the incident is assigned to.",
        )
        owner.owner_type = AAZStrArg(
            options=["owner-type"],
            help="The type of the owner the incident is assigned to.",
            enum={"Group": "Group", "Unknown": "Unknown", "User": "User"},
        )
        owner.user_principal_name = AAZStrArg(
            options=["user-principal-name"],
            help="The user principal name of the user the incident is assigned to.",
        )

        run_playbook = cls._args_schema.actions.Element.run_playbook
        run_playbook.action_configuration = AAZObjectArg(
            options=["action-configuration"],
        )

        action_configuration = cls._args_schema.actions.Element.run_playbook.action_configuration
        action_configuration.logic_app_resource_id = AAZStrArg(
            options=["logic-app-resource-id"],
            help="The resource id of the playbook resource",
        )
        action_configuration.tenant_id = AAZStrArg(
            options=["tenant-id"],
            help="The tenant id of the playbook resource",
        )

        triggering_logic = cls._args_schema.triggering_logic
        triggering_logic.conditions = AAZListArg(
            options=["conditions"],
            singular_options=["condition"],
            help="The conditions to evaluate to determine if the automation rule should be triggered on a given object",
        )
        triggering_logic.expiration_time_utc = AAZStrArg(
            options=["expiration-time-utc"],
            help="Determines when the automation rule should automatically expire and be disabled.",
        )
        triggering_logic.is_enabled = AAZBoolArg(
            options=["is-enabled"],
            help="Determines whether the automation rule is enabled or disabled",
        )
        triggering_logic.triggers_on = AAZStrArg(
            options=["triggers-on"],
            enum={"Incidents": "Incidents"},
        )
        triggering_logic.triggers_when = AAZStrArg(
            options=["triggers-when"],
            enum={"Created": "Created"},
        )

        conditions = cls._args_schema.triggering_logic.conditions
        conditions.Element = AAZObjectArg()

        _element = cls._args_schema.triggering_logic.conditions.Element
        _element.property = AAZObjectArg(
            options=["property"],
        )

        property = cls._args_schema.triggering_logic.conditions.Element.property
        property.condition_properties = AAZObjectArg(
            options=["condition-properties"],
        )

        condition_properties = cls._args_schema.triggering_logic.conditions.Element.property.condition_properties
        condition_properties.operator = AAZStrArg(
            options=["operator"],
            enum={"Contains": "Contains", "EndsWith": "EndsWith", "Equals": "Equals", "NotContains": "NotContains", "NotEndsWith": "NotEndsWith", "NotEquals": "NotEquals", "NotStartsWith": "NotStartsWith", "StartsWith": "StartsWith"},
        )
        condition_properties.property_name = AAZStrArg(
            options=["property-name"],
            help="The property to evaluate in an automation rule property condition",
            enum={"AccountAadTenantId": "AccountAadTenantId", "AccountAadUserId": "AccountAadUserId", "AccountNTDomain": "AccountNTDomain", "AccountName": "AccountName", "AccountObjectGuid": "AccountObjectGuid", "AccountPUID": "AccountPUID", "AccountSid": "AccountSid", "AccountUPNSuffix": "AccountUPNSuffix", "AlertProductNames": "AlertProductNames", "AzureResourceResourceId": "AzureResourceResourceId", "AzureResourceSubscriptionId": "AzureResourceSubscriptionId", "CloudApplicationAppId": "CloudApplicationAppId", "CloudApplicationAppName": "CloudApplicationAppName", "DNSDomainName": "DNSDomainName", "FileDirectory": "FileDirectory", "FileHashValue": "FileHashValue", "FileName": "FileName", "HostAzureID": "HostAzureID", "HostNTDomain": "HostNTDomain", "HostName": "HostName", "HostNetBiosName": "HostNetBiosName", "HostOSVersion": "HostOSVersion", "IPAddress": "IPAddress", "IncidentDescription": "IncidentDescription", "IncidentLabel": "IncidentLabel", "IncidentProviderName": "IncidentProviderName", "IncidentRelatedAnalyticRuleIds": "IncidentRelatedAnalyticRuleIds", "IncidentSeverity": "IncidentSeverity", "IncidentStatus": "IncidentStatus", "IncidentTactics": "IncidentTactics", "IncidentTitle": "IncidentTitle", "IoTDeviceId": "IoTDeviceId", "IoTDeviceModel": "IoTDeviceModel", "IoTDeviceName": "IoTDeviceName", "IoTDeviceOperatingSystem": "IoTDeviceOperatingSystem", "IoTDeviceType": "IoTDeviceType", "IoTDeviceVendor": "IoTDeviceVendor", "MailMessageDeliveryAction": "MailMessageDeliveryAction", "MailMessageDeliveryLocation": "MailMessageDeliveryLocation", "MailMessageP1Sender": "MailMessageP1Sender", "MailMessageP2Sender": "MailMessageP2Sender", "MailMessageRecipient": "MailMessageRecipient", "MailMessageSenderIP": "MailMessageSenderIP", "MailMessageSubject": "MailMessageSubject", "MailboxDisplayName": "MailboxDisplayName", "MailboxPrimaryAddress": "MailboxPrimaryAddress", "MailboxUPN": "MailboxUPN", "MalwareCategory": "MalwareCategory", "MalwareName": "MalwareName", "ProcessCommandLine": "ProcessCommandLine", "ProcessId": "ProcessId", "RegistryKey": "RegistryKey", "RegistryValueData": "RegistryValueData", "Url": "Url"},
        )
        condition_properties.property_values = AAZListArg(
            options=["property-values"],
            singular_options=["property-value"],
        )

        property_values = cls._args_schema.triggering_logic.conditions.Element.property.condition_properties.property_values
        property_values.Element = AAZStrArg()
        return cls._args_schema

    def _execute_operations(self):
        self.AutomationRulesGet(ctx=self.ctx)()
        self.InstanceUpdateByJson(ctx=self.ctx)()
        self.InstanceUpdateByGeneric(ctx=self.ctx)()
        self.AutomationRulesCreateOrUpdate(ctx=self.ctx)()

    def _output(self, *args, **kwargs):
        result = self.deserialize_output(self.ctx.vars.instance, client_flatten=True)
        return result

    class AutomationRulesGet(AAZHttpOperation):
        CLIENT_TYPE = "MgmtClient"

        def __call__(self, *args, **kwargs):
            request = self.make_request()
            session = self.client.send_request(request=request, stream=False, **kwargs)
            if session.http_response.status_code in [200]:
                return self.on_200(session)

            return self.on_error(session.http_response)

        @property
        def url(self):
            return self.client.format_url(
                "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.OperationalInsights/workspaces/{workspaceName}/providers/Microsoft.SecurityInsights/automationRules/{automationRuleId}",
                **self.url_parameters
            )

        @property
        def method(self):
            return "GET"

        @property
        def error_format(self):
            return "ODataV4Format"

        @property
        def url_parameters(self):
            parameters = {
                **self.serialize_url_param(
                    "automationRuleId", self.ctx.args.automation_rule_id,
                    required=True,
                ),
                **self.serialize_url_param(
                    "resourceGroupName", self.ctx.args.resource_group,
                    required=True,
                ),
                **self.serialize_url_param(
                    "subscriptionId", self.ctx.subscription_id,
                    required=True,
                ),
                **self.serialize_url_param(
                    "workspaceName", self.ctx.args.workspace_name,
                    required=True,
                ),
            }
            return parameters

        @property
        def query_parameters(self):
            parameters = {
                **self.serialize_query_param(
                    "api-version", "2021-10-01",
                    required=True,
                ),
            }
            return parameters

        @property
        def header_parameters(self):
            parameters = {
                **self.serialize_header_param(
                    "Accept", "application/json",
                ),
            }
            return parameters

        def on_200(self, session):
            data = self.deserialize_http_content(session)
            self.ctx.set_var(
                "instance",
                data,
                schema_builder=self._build_schema_on_200
            )

        _schema_on_200 = None

        @classmethod
        def _build_schema_on_200(cls):
            if cls._schema_on_200 is not None:
                return cls._schema_on_200

            cls._schema_on_200 = AAZObjectType()
            _build_schema_automation_rule_read(cls._schema_on_200)

            return cls._schema_on_200

    class AutomationRulesCreateOrUpdate(AAZHttpOperation):
        CLIENT_TYPE = "MgmtClient"

        def __call__(self, *args, **kwargs):
            request = self.make_request()
            session = self.client.send_request(request=request, stream=False, **kwargs)
            if session.http_response.status_code in [200, 201]:
                return self.on_200_201(session)

            return self.on_error(session.http_response)

        @property
        def url(self):
            return self.client.format_url(
                "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.OperationalInsights/workspaces/{workspaceName}/providers/Microsoft.SecurityInsights/automationRules/{automationRuleId}",
                **self.url_parameters
            )

        @property
        def method(self):
            return "PUT"

        @property
        def error_format(self):
            return "ODataV4Format"

        @property
        def url_parameters(self):
            parameters = {
                **self.serialize_url_param(
                    "automationRuleId", self.ctx.args.automation_rule_id,
                    required=True,
                ),
                **self.serialize_url_param(
                    "resourceGroupName", self.ctx.args.resource_group,
                    required=True,
                ),
                **self.serialize_url_param(
                    "subscriptionId", self.ctx.subscription_id,
                    required=True,
                ),
                **self.serialize_url_param(
                    "workspaceName", self.ctx.args.workspace_name,
                    required=True,
                ),
            }
            return parameters

        @property
        def query_parameters(self):
            parameters = {
                **self.serialize_query_param(
                    "api-version", "2021-10-01",
                    required=True,
                ),
            }
            return parameters

        @property
        def header_parameters(self):
            parameters = {
                **self.serialize_header_param(
                    "Content-Type", "application/json",
                ),
                **self.serialize_header_param(
                    "Accept", "application/json",
                ),
            }
            return parameters

        @property
        def content(self):
            _content_value, _builder = self.new_content_builder(
                self.ctx.args,
                value=self.ctx.vars.instance,
            )

            return self.serialize_content(_content_value)

        def on_200_201(self, session):
            data = self.deserialize_http_content(session)
            self.ctx.set_var(
                "instance",
                data,
                schema_builder=self._build_schema_on_200_201
            )

        _schema_on_200_201 = None

        @classmethod
        def _build_schema_on_200_201(cls):
            if cls._schema_on_200_201 is not None:
                return cls._schema_on_200_201

            cls._schema_on_200_201 = AAZObjectType()
            _build_schema_automation_rule_read(cls._schema_on_200_201)

            return cls._schema_on_200_201

    class InstanceUpdateByJson(AAZJsonInstanceUpdateOperation):

        def __call__(self, *args, **kwargs):
            self._update_instance(self.ctx.vars.instance)

        def _update_instance(self, instance):
            _instance_value, _builder = self.new_content_builder(
                self.ctx.args,
                value=instance,
                typ=AAZObjectType
            )
            _builder.set_prop("etag", AAZStrType, ".etag")
            _builder.set_prop("properties", AAZObjectType, ".", typ_kwargs={"flags": {"required": True, "client_flatten": True}})

            properties = _builder.get(".properties")
            if properties is not None:
                properties.set_prop("actions", AAZListType, ".actions", typ_kwargs={"flags": {"required": True}})
                properties.set_prop("displayName", AAZStrType, ".display_name", typ_kwargs={"flags": {"required": True}})
                properties.set_prop("order", AAZIntType, ".order", typ_kwargs={"flags": {"required": True}})
                properties.set_prop("triggeringLogic", AAZObjectType, ".triggering_logic", typ_kwargs={"flags": {"required": True}})

            actions = _builder.get(".properties.actions")
            if actions is not None:
                actions.set_elements(AAZObjectType)

            _elements = _builder.get(".properties.actions[]")
            if _elements is not None:
                _elements.set_const("actionType", "ModifyProperties", AAZStrType, ".modify_properties", typ_kwargs={"flags": {"required": True}})
                _elements.set_const("actionType", "RunPlaybook", AAZStrType, ".run_playbook", typ_kwargs={"flags": {"required": True}})
                _elements.set_prop("order", AAZIntType, ".order", typ_kwargs={"flags": {"required": True}})
                _elements.discriminate_by("actionType", "ModifyProperties")
                _elements.discriminate_by("actionType", "RunPlaybook")

            disc_modify_properties = _builder.get(".properties.actions[]{actionType:ModifyProperties}")
            if disc_modify_properties is not None:
                disc_modify_properties.set_prop("actionConfiguration", AAZObjectType, ".modify_properties.action_configuration")

            action_configuration = _builder.get(".properties.actions[]{actionType:ModifyProperties}.actionConfiguration")
            if action_configuration is not None:
                action_configuration.set_prop("classification", AAZStrType, ".classification")
                action_configuration.set_prop("classificationComment", AAZStrType, ".classification_comment")
                action_configuration.set_prop("classificationReason", AAZStrType, ".classification_reason")
                action_configuration.set_prop("labels", AAZListType, ".labels")
                action_configuration.set_prop("owner", AAZObjectType, ".owner")
                action_configuration.set_prop("severity", AAZStrType, ".severity")
                action_configuration.set_prop("status", AAZStrType, ".status")

            labels = _builder.get(".properties.actions[]{actionType:ModifyProperties}.actionConfiguration.labels")
            if labels is not None:
                labels.set_elements(AAZObjectType)

            _elements = _builder.get(".properties.actions[]{actionType:ModifyProperties}.actionConfiguration.labels[]")
            if _elements is not None:
                _elements.set_prop("labelName", AAZStrType, ".label_name", typ_kwargs={"flags": {"required": True}})

            owner = _builder.get(".properties.actions[]{actionType:ModifyProperties}.actionConfiguration.owner")
            if owner is not None:
                owner.set_prop("assignedTo", AAZStrType, ".assigned_to")
                owner.set_prop("email", AAZStrType, ".email")
                owner.set_prop("objectId", AAZStrType, ".object_id")
                owner.set_prop("ownerType", AAZStrType, ".owner_type")
                owner.set_prop("userPrincipalName", AAZStrType, ".user_principal_name")

            disc_run_playbook = _builder.get(".properties.actions[]{actionType:RunPlaybook}")
            if disc_run_playbook is not None:
                disc_run_playbook.set_prop("actionConfiguration", AAZObjectType, ".run_playbook.action_configuration")

            action_configuration = _builder.get(".properties.actions[]{actionType:RunPlaybook}.actionConfiguration")
            if action_configuration is not None:
                action_configuration.set_prop("logicAppResourceId", AAZStrType, ".logic_app_resource_id", typ_kwargs={"flags": {"required": True}})
                action_configuration.set_prop("tenantId", AAZStrType, ".tenant_id")

            triggering_logic = _builder.get(".properties.triggeringLogic")
            if triggering_logic is not None:
                triggering_logic.set_prop("conditions", AAZListType, ".conditions")
                triggering_logic.set_prop("expirationTimeUtc", AAZStrType, ".expiration_time_utc")
                triggering_logic.set_prop("isEnabled", AAZBoolType, ".is_enabled", typ_kwargs={"flags": {"required": True}})
                triggering_logic.set_prop("triggersOn", AAZStrType, ".triggers_on", typ_kwargs={"flags": {"required": True}})
                triggering_logic.set_prop("triggersWhen", AAZStrType, ".triggers_when", typ_kwargs={"flags": {"required": True}})

            conditions = _builder.get(".properties.triggeringLogic.conditions")
            if conditions is not None:
                conditions.set_elements(AAZObjectType)

            _elements = _builder.get(".properties.triggeringLogic.conditions[]")
            if _elements is not None:
                _elements.set_const("conditionType", "Property", AAZStrType, ".property", typ_kwargs={"flags": {"required": True}})
                _elements.discriminate_by("conditionType", "Property")

            disc_property = _builder.get(".properties.triggeringLogic.conditions[]{conditionType:Property}")
            if disc_property is not None:
                disc_property.set_prop("conditionProperties", AAZObjectType, ".property.condition_properties")

            condition_properties = _builder.get(".properties.triggeringLogic.conditions[]{conditionType:Property}.conditionProperties")
            if condition_properties is not None:
                condition_properties.set_prop("operator", AAZStrType, ".operator")
                condition_properties.set_prop("propertyName", AAZStrType, ".property_name")
                condition_properties.set_prop("propertyValues", AAZListType, ".property_values")

            property_values = _builder.get(".properties.triggeringLogic.conditions[]{conditionType:Property}.conditionProperties.propertyValues")
            if property_values is not None:
                property_values.set_elements(AAZStrType, ".")

            return _instance_value

    class InstanceUpdateByGeneric(AAZGenericInstanceUpdateOperation):

        def __call__(self, *args, **kwargs):
            self._update_instance_by_generic(
                self.ctx.vars.instance,
                self.ctx.generic_update_args
            )


_schema_automation_rule_read = None


def _build_schema_automation_rule_read(_schema):
    global _schema_automation_rule_read
    if _schema_automation_rule_read is not None:
        _schema.etag = _schema_automation_rule_read.etag
        _schema.id = _schema_automation_rule_read.id
        _schema.name = _schema_automation_rule_read.name
        _schema.properties = _schema_automation_rule_read.properties
        _schema.system_data = _schema_automation_rule_read.system_data
        _schema.type = _schema_automation_rule_read.type
        return

    _schema_automation_rule_read = AAZObjectType()

    automation_rule_read = _schema_automation_rule_read
    automation_rule_read.etag = AAZStrType()
    automation_rule_read.id = AAZStrType(
        flags={"read_only": True},
    )
    automation_rule_read.name = AAZStrType(
        flags={"read_only": True},
    )
    automation_rule_read.properties = AAZObjectType(
        flags={"required": True, "client_flatten": True},
    )
    automation_rule_read.system_data = AAZObjectType(
        serialized_name="systemData",
        flags={"read_only": True},
    )
    automation_rule_read.type = AAZStrType(
        flags={"read_only": True},
    )

    properties = _schema_automation_rule_read.properties
    properties.actions = AAZListType(
        flags={"required": True},
    )
    properties.created_by = AAZObjectType(
        serialized_name="createdBy",
        flags={"read_only": True},
    )
    _build_schema_client_info_read(properties.created_by)
    properties.created_time_utc = AAZStrType(
        serialized_name="createdTimeUtc",
        flags={"read_only": True},
    )
    properties.display_name = AAZStrType(
        serialized_name="displayName",
        flags={"required": True},
    )
    properties.last_modified_by = AAZObjectType(
        serialized_name="lastModifiedBy",
        flags={"read_only": True},
    )
    _build_schema_client_info_read(properties.last_modified_by)
    properties.last_modified_time_utc = AAZStrType(
        serialized_name="lastModifiedTimeUtc",
        flags={"read_only": True},
    )
    properties.order = AAZIntType(
        flags={"required": True},
    )
    properties.triggering_logic = AAZObjectType(
        serialized_name="triggeringLogic",
        flags={"required": True},
    )

    actions = _schema_automation_rule_read.properties.actions
    actions.Element = AAZObjectType()

    _element = _schema_automation_rule_read.properties.actions.Element
    _element.action_type = AAZStrType(
        serialized_name="actionType",
        flags={"required": True},
    )
    _element.order = AAZIntType(
        flags={"required": True},
    )

    disc_modify_properties = _schema_automation_rule_read.properties.actions.Element.discriminate_by("action_type", "ModifyProperties")
    disc_modify_properties.action_configuration = AAZObjectType(
        serialized_name="actionConfiguration",
    )

    action_configuration = _schema_automation_rule_read.properties.actions.Element.discriminate_by("action_type", "ModifyProperties").action_configuration
    action_configuration.classification = AAZStrType()
    action_configuration.classification_comment = AAZStrType(
        serialized_name="classificationComment",
    )
    action_configuration.classification_reason = AAZStrType(
        serialized_name="classificationReason",
    )
    action_configuration.labels = AAZListType()
    action_configuration.owner = AAZObjectType()
    action_configuration.severity = AAZStrType()
    action_configuration.status = AAZStrType()

    labels = _schema_automation_rule_read.properties.actions.Element.discriminate_by("action_type", "ModifyProperties").action_configuration.labels
    labels.Element = AAZObjectType()

    _element = _schema_automation_rule_read.properties.actions.Element.discriminate_by("action_type", "ModifyProperties").action_configuration.labels.Element
    _element.label_name = AAZStrType(
        serialized_name="labelName",
        flags={"required": True},
    )
    _element.label_type = AAZStrType(
        serialized_name="labelType",
        flags={"read_only": True},
    )

    owner = _schema_automation_rule_read.properties.actions.Element.discriminate_by("action_type", "ModifyProperties").action_configuration.owner
    owner.assigned_to = AAZStrType(
        serialized_name="assignedTo",
    )
    owner.email = AAZStrType()
    owner.object_id = AAZStrType(
        serialized_name="objectId",
    )
    owner.owner_type = AAZStrType(
        serialized_name="ownerType",
    )
    owner.user_principal_name = AAZStrType(
        serialized_name="userPrincipalName",
    )

    disc_run_playbook = _schema_automation_rule_read.properties.actions.Element.discriminate_by("action_type", "RunPlaybook")
    disc_run_playbook.action_configuration = AAZObjectType(
        serialized_name="actionConfiguration",
    )

    action_configuration = _schema_automation_rule_read.properties.actions.Element.discriminate_by("action_type", "RunPlaybook").action_configuration
    action_configuration.logic_app_resource_id = AAZStrType(
        serialized_name="logicAppResourceId",
        flags={"required": True},
    )
    action_configuration.tenant_id = AAZStrType(
        serialized_name="tenantId",
    )

    triggering_logic = _schema_automation_rule_read.properties.triggering_logic
    triggering_logic.conditions = AAZListType()
    triggering_logic.expiration_time_utc = AAZStrType(
        serialized_name="expirationTimeUtc",
    )
    triggering_logic.is_enabled = AAZBoolType(
        serialized_name="isEnabled",
        flags={"required": True},
    )
    triggering_logic.triggers_on = AAZStrType(
        serialized_name="triggersOn",
        flags={"required": True},
    )
    triggering_logic.triggers_when = AAZStrType(
        serialized_name="triggersWhen",
        flags={"required": True},
    )

    conditions = _schema_automation_rule_read.properties.triggering_logic.conditions
    conditions.Element = AAZObjectType()

    _element = _schema_automation_rule_read.properties.triggering_logic.conditions.Element
    _element.condition_type = AAZStrType(
        serialized_name="conditionType",
        flags={"required": True},
    )

    disc_property = _schema_automation_rule_read.properties.triggering_logic.conditions.Element.discriminate_by("condition_type", "Property")
    disc_property.condition_properties = AAZObjectType(
        serialized_name="conditionProperties",
    )

    condition_properties = _schema_automation_rule_read.properties.triggering_logic.conditions.Element.discriminate_by("condition_type", "Property").condition_properties
    condition_properties.operator = AAZStrType()
    condition_properties.property_name = AAZStrType(
        serialized_name="propertyName",
    )
    condition_properties.property_values = AAZListType(
        serialized_name="propertyValues",
    )

    property_values = _schema_automation_rule_read.properties.triggering_logic.conditions.Element.discriminate_by("condition_type", "Property").condition_properties.property_values
    property_values.Element = AAZStrType()

    system_data = _schema_automation_rule_read.system_data
    system_data.created_at = AAZStrType(
        serialized_name="createdAt",
        flags={"read_only": True},
    )
    system_data.created_by = AAZStrType(
        serialized_name="createdBy",
        flags={"read_only": True},
    )
    system_data.created_by_type = AAZStrType(
        serialized_name="createdByType",
        flags={"read_only": True},
    )
    system_data.last_modified_at = AAZStrType(
        serialized_name="lastModifiedAt",
        flags={"read_only": True},
    )
    system_data.last_modified_by = AAZStrType(
        serialized_name="lastModifiedBy",
        flags={"read_only": True},
    )
    system_data.last_modified_by_type = AAZStrType(
        serialized_name="lastModifiedByType",
        flags={"read_only": True},
    )

    _schema.etag = _schema_automation_rule_read.etag
    _schema.id = _schema_automation_rule_read.id
    _schema.name = _schema_automation_rule_read.name
    _schema.properties = _schema_automation_rule_read.properties
    _schema.system_data = _schema_automation_rule_read.system_data
    _schema.type = _schema_automation_rule_read.type


_schema_client_info_read = None


def _build_schema_client_info_read(_schema):
    global _schema_client_info_read
    if _schema_client_info_read is not None:
        _schema.email = _schema_client_info_read.email
        _schema.name = _schema_client_info_read.name
        _schema.object_id = _schema_client_info_read.object_id
        _schema.user_principal_name = _schema_client_info_read.user_principal_name
        return

    _schema_client_info_read = AAZObjectType(
        flags={"read_only": True}
    )

    client_info_read = _schema_client_info_read
    client_info_read.email = AAZStrType(
        flags={"read_only": True},
    )
    client_info_read.name = AAZStrType(
        flags={"read_only": True},
    )
    client_info_read.object_id = AAZStrType(
        serialized_name="objectId",
        flags={"read_only": True},
    )
    client_info_read.user_principal_name = AAZStrType(
        serialized_name="userPrincipalName",
        flags={"read_only": True},
    )

    _schema.email = _schema_client_info_read.email
    _schema.name = _schema_client_info_read.name
    _schema.object_id = _schema_client_info_read.object_id
    _schema.user_principal_name = _schema_client_info_read.user_principal_name


__all__ = ["Update"]
