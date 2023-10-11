# Microsoft Atomic Azure CLI Dev Tools

The *aaz-dev* tool is designed to generate atomic Azure CLI commands from OpenAPI specifications. For more information, please refer to [document](https://azure.github.io/aaz-dev-tools/) and [video](https://msit.microsoftstream.com/video/d8c50840-98dc-a27a-806a-f1ed2daa33a9).

## Installation
Currently, we can install it with a [.whl file](https://github.com/Azure/aaz-dev-tools/releases). Later on, we'll publish it to PyPI to support *pip install* way of installation.

## Setting up your development environment

### 1 Code repos

Please `Fork` the following repos in your github account and `Clone` them in your local disk:
   
   - [Azure CLI](https://github.com/Azure/azure-cli)
   - [Azure CLI Extension](https://github.com/Azure/azure-cli-extensions)
   - [AAZ](https://github.com/Azure/aaz): Used to upload the command model generated.
   - [azure-rest-api-specs](https://github.com/Azure/azure-rest-api-specs) or [azure-rest-api-specs-pr](https://github.com/Azure/azure-rest-api-specs-pr)

After clone you can add `upstream` for every repos in your local clone by using `git remote add upstream`.

### 2 Setup python

#### 2.1 Install python
Please install python with version >= 3.8 in your local machine.

- For windows: You can download and run full installer from [Python Download](https://www.python.org/downloads/).
- For linux: You can install python from Package Manager or build a stable relase from source code

Check the version of python, make use it's not less than 3.8.
- For windows:
    You can run:
    ```PowerShell
    C:\Users\{xxxx}\AppData\Local\Programs\Python\Python3{xxxx}\python --version
    ```
    `C:\Users\{xxxx}\AppData\Local\Programs\Python\Python3{xxxx}` is the python installation path.
- For linux:
    ```bash
    python --version
    ```
    You can also specify the version number when you have multiple versions installed. For example if you want to run version 3.8
    ```bash
    python3.8 --version
    ```

#### 2.2 Setup a python virtual environment

You can use venv to create virtual environments, optionally isolated from system site directories. Each virtual environment has its own Python binary (which matches the version of the binary that was used to create this environment) and can have its own independent set of installed Python packages in its site directories.

You can run the following command to create a new virtual environment:
- For windows:
    ```PowerShell
    C:\Users\{xxxx}\AppData\Local\Programs\Python\Python3{xxxx}\python -m venv {some path}\{venv name}
    ```
- For linux:
    ```bash
    python3.8 -m venv {some path}/{venv name}
    ```

### 3 Active existing virtual environment

You should __always__ active the virtual environment for azure-cli development.

- For Windows:
    - Powershell
    ```powershell
    {some path}\{venv name}\Scripts\Activate.ps1
    ```
    - Command Prompt
    ```Command Prompt
    {some path}\{venv name}\Scripts\activate.bat
    ```
- For Linux:
```bash
source {some path}/{venv name}/bin/activate
```
After active the virtual environment, the `python` command will always be the one creates this virtual environment and you can always use `python`
```
python --version
```

### 4 Install tools for azure-cli development

#### 4.1 Install [azure-cli-dev-tools](https://github.com/Azure/azure-cli-dev-tools)
Both for windows and linux
```
pip install azdev
```

#### 4.2 Install aaz-dev-tools

- For Windows
    - Powershell
    ```
    pip install aaz-dev
    ```
    - Command Prompt
    ```
    pip install aaz-dev
    ```
- For linux
    ```bash
    pip install aaz-dev
    ```
#### 4.3 Set up build env
- For linux users, set up python3 build tools would avoid other unseen installation issues
  ```
  Ubuntu: apt-get install python3-dev build-essential
  Centos: yum install python3-devel
  ```
#### 4.4 Possible problems
- For windows users, dependency python-levenshtein installation might run into trouble. developers might need to download [.whl](https://www.lfd.uci.edu/~gohlke/pythonlibs/#python-levenshtein) file and install it manually (reference to [link](https://stackoverflow.com/questions/37676623/cant-install-levenshtein-distance-package-on-windows-python-3-5/46414982))

### 5. Code repos setup

#### 5.1 azure-cli
Before start to the development task, you should always sync the code in the `dev` branch of `upstream`(Azure/Azure-cli).
If your commands will generated to azure-cli repo, you should checkout a new branch with `feature-` prefix.

#### 5.2 azure-cli-extensions
If your commands will generated to azure-cli-extension repo, you should sync the code in the `main` branch of `upstream`(Azure/Azure-cli-extensions), and checkout a new branch with `feature-` prefix.

#### 5.3 aaz
Before start to the development task, you should always sync the change in the `main` branch of `upstream`, and checkout a new branch with `feature-` prefix.

#### 5.4 run `azdev setup`
You should always run the following command everytime you sync `azure-cli` code of `upstream`.
```
azdev setup --cli {path to azure-cli} --repo {path to azure-cli-extensions}
```

### 6 Run aaz-dev-tools

```bash
aaz-dev run -c {path to azure-cli} -e {path to azure-cli-extensions} -s {path swagger or swagger-pr} -a {path to aaz}
```

## Before using generated commands

1. Make sure you have logined by `az login`.
2. Make sure you have switched to the subscription for test by `az account set -s {subscription ID for test}`
3. If your commands are in extensions, make sure you have loaded this extension by `azdev extension add {your extension name}`

## Other documentations

- [extension](https://github.com/Azure/azure-cli/blob/dev/doc/extensions/README.md)
- [command guidelines](https://github.com/Azure/azure-cli/blob/dev/doc/command_guidelines.md)
- [authoring tests](https://github.com/Azure/azure-cli/blob/dev/doc/authoring_tests.md)
- [shorthand syntax](https://github.com/Azure/azure-cli/blob/dev/doc/shorthand_syntax.md): Azure cli shorthand syntax can help cli users to pass complicated argument values. Only the arguments of AAZ(Atomic Azure CLI) commands generated by aaz-dev tool support shorthand syntax.

## Submit code and command models

After finish the development, you should push the change in your forked repos first, and the create a Pull Request to upstream repos.

- azure-cli: create a Pull Request to `dev` branch of `Azure/azure-cli`
- azure-cli-extensions: create a Pull Request to `main` branch of `Azure/azure-cli-extensions` 
- aaz: create a Pull Request to `main` branch of `Azure/azz`


## Reporting issues and feedback
If you encounter any bugs with the tool please file an issue in the [Issues](https://github.com/Azure/aaz-dev-tools/issues) section of our GitHub repository.

## License
```
MIT License

Copyright (c) Microsoft Corporation. All rights reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the ""Software""), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```
