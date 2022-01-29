# monitor clone `[Command]`

Clone metrics alert rules from one resource to another resource.

Long Summery Line 1\
Long Summery Line 2\
Long Summery End Line

## Versions

### [2019-01-03](/docs/specs/Resources/mgmt-plane/L3N1YnNjcmlwdGlvbnMve30vcHJvdmlkZXJzL21pY3Jvc29mdC5lZGdlb3JkZXIvYWRkcmVzc2Vz/2019-03-01.xml) `Preview`

#### Examples

- Clone the metric alert settings from one VM to another

    ```bash
    az monitor clone --source-resource /subscriptions/{subscriptionID}/resourceGroups/Space1999/
            providers/Microsoft.Compute/virtualMachines/vm1 --target-resource /subscriptions/{subscripti
            onID}/resourceGroups/Space1999/providers/Microsoft.Compute/virtualMachines/vm2
    ```

- Clone the metric alert settings from one VM to another

    ```bash
    az monitor clone --source-resource /subscriptions/{subscriptionID}/resourceGroups/Space1999/
            providers/Microsoft.Compute/virtualMachines/vm1 --target-resource /subscriptions/{subscripti
            onID}/resourceGroups/Space1999/providers/Microsoft.Compute/virtualMachines/vm2
    ```

    