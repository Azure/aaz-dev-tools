# Microsoft Atomic Azure CLI Dev Tools

The *aaz-dev* tool is designed to generate atomic Azure CLI commands from OpenAPI specifications. For more information, please refer to [detailed documentation](https://github.com/necusjz/aaz-dev-tools/tree/release-pipeline/src/backend/docs/Docs). 

## Installation
Currently, we can install it with a [.whl file](https://github.com/kairu-ms/aaz-dev-tools/releases). Later on, we'll publish it to PyPI to support *pip install* way of installation.

## Setting up your development environment
1. Fork and clone the repositories that will be needed later:
   - For Azure CLI: Azure CLI: https://github.com/Azure/azure-cli;
   - For Azure CLI Extension: https://github.com/Azure/azure-cli-extensions (or any other repository that you might have access to that contains CLI extensions);
   - For Swagger Specs: https://github.com/Azure/azure-rest-api-specs (or private one: https://github.com/Azure/azure-rest-api-specs-pr);
   - For AAZ: https://github.com/kairu-ms/aaz;

2. Install python(>= 3.8) and create an virtual environment for azure-cli development
```bash
python3 -m venv /path/to/new/azure-cli-venv
```

3. Active venv

Windows powershell
```powershell
.\path\to\new\azure-cli-venv\Scripts\Activate.ps1
```

Linux bash
```bash
source /path/to/new/azure-cli-venv/bin/activate
```

4. Install [azure-cli-dev-tools](https://github.com/Azure/azure-cli-dev-tools) and setup azure-cli environment
```bash
pip install azdev
azdev setup -c /path/to/azure-cli -r /path/to/azure-cli-extensions
```

5. Install aaz-dev-tools
```bash
AAZDevVersion=0.1.0
pip install https://github.com/kairu-ms/aaz-dev-tools/releases/download/v$AAZDevVersion/aaz_dev-$AAZDevVersion-py3-none-any.whl
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
