# Microsoft Atomic Azure CLI Dev Tools

The *aaz-dev* tool is designed to generate atomic Azure CLI commands from OpenAPI specifications. For more information, please refer to [detailed documentation](https://github.com/necusjz/aaz-dev-tools/tree/release-pipeline/src/backend/docs/Docs). 

## Installation
Currently, we can install it with a [.whl file](https://github.com/kairu-ms/aaz-dev-tools/releases). Later on, we'll publish it to PyPI to support *pip install* way of installation.

## Setting up your development environment

### Code repos

1. Please `Fork` the following repos in your github account and `Clone` them in your local disk:
   - [Azure CLI](https://github.com/Azure/azure-cli)
   - [Azure CLI Extension](https://github.com/Azure/azure-cli-extensions)
   - [AAZ](https://github.com/kairu-ms/aaz): Used to upload the command model generated.
   - [azure-rest-api-specs](https://github.com/Azure/azure-rest-api-specs) or [azure-rest-api-specs-pr](https://github.com/Azure/azure-rest-api-specs-pr)

2. Add upstream for every repos in your local clone by using command:
```
git remote add upstream {upstream url}
```


2. Install python(>= 3.8)
    - Install python in windows: Download and run full installer from [Python Download](https://www.python.org/downloads/).
    

2. Install python(>= 3.8) and create an virtual environment for azure-cli development


```bash
python3 -m venv /path/to/new/azure-cli-venv
```

3. Active venv

For Windows powershell
```powershell
.\path\to\new\azure-cli-venv\Scripts\Activate.ps1
```

For Linux bash
```bash
source /path/to/new/azure-cli-venv/bin/activate
```

4. Install [azure-cli-dev-tools](https://github.com/Azure/azure-cli-dev-tools) and setup azure-cli environment
```bash
pip install azdev
azdev setup -c /path/to/azure-cli -r /path/to/azure-cli-extensions
```

5. Install aaz-dev-tools

For Command Prompt

For powershell
```bash

```

For bash
```bash
pip install $(curl https://api.github.com/repos/kairu-ms/aaz-dev-tools/releases/latest -s | grep -o "https.*.whl")
```

## Run aaz-dev tool

Show help message of `aaz-dev run`
```bash
aaz-dev run --help
```

Run `aaz-dev`
```bash
aaz-dev run -c /path/to/azure-cli -e /path/to/azure-cli-extensions -s /path/to/swagger -a /path/to/aaz
```

## Reporting issues and feedback
If you encounter any bugs with the tool please file an issue in the [Issues](https://github.com/kairu-ms/aaz-dev-tools/issues) section of our GitHub repository.

## License
```
MIT License

Copyright (c) Microsoft Corporation. All rights reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the ""Software""), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```
