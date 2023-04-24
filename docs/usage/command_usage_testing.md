# Command Usage/Testing

## Overview

Azure CLI provides two types of tests we can use: [unit tests](https://en.wikipedia.org/wiki/Unit_testing) and  [integration tests](https://en.wikipedia.org/wiki/Integration_testing).

For unit tests, we support unit tests written in the forms standard [unittest](https://docs.python.org/3/library/unittest.html).

For integration tests, we provide the `ScenarioTest` and `LiveScenarioTest` classes to support replayable tests via [VCR.py](https://vcrpy.readthedocs.io/en/latest/).

Details about these two types of testing, env preparation, test policies and issue troubleshooting, please refer to the [doc](https://github.com/Azure/azure-cli/blob/dev/doc/authoring_tests.md)

After generating code from CodeGenV2, target cmd's test can be added into folder `path/to/your/cloned/azure-cli/target_mod`. Below is the demonstration of tests using azdev and [Pycharm Community](https://www.jetbrains.com/pycharm/download/#section=linux)
### 1. unit test
When first run unit test, use `--live` to access api and record `yaml` file for integration tests.
```
live mode: azdev test test_function_of_your_code --live
non-live mode: azdev test test_function_of_your_code
```
For issues debugging, use `--debug` parameter appended the above cmd. 

For Pycharm Community, set env `Azure_TEST_RUN_LIVE` to be `true` for live mode and `false` for non-live mode.

![pycharm_env](/Docs/images/pycharm_live.png)

### 2. intergration test
Run tests for specific modules
```
azdev test {mod1} {mod2}
```
Re-run the tests that failed the previous run.
```
azdev test --lf
```
For more details about using `azdev`, please check message of `azdev test --help` 

### 3. Cmd usage
1. Before using the generated cmd, `az login` and `az account set -s your-subscription-id` should be set properly as noted [here](https://github.com/Azure/aaz-dev-tools#before-using-generated-commands)
2. Run generated cmd `az your-module your-cmd`
3. For issue debugging, please use `az your-module your-cmd --debug` to check the error and fix it. If more help or instruction needed, please leave a message to us with the error info printed in console.