---
layout: page
title: Local Development Guide
permalink: /pages/usage/local-dev-guide/
weight: 105
---

## Prerequisites

- [Python 3.9+](https://www.python.org/downloads/)
- [Node.js 22+](https://nodejs.org/) (required by the vendored TypeSpec 1.13 submodule)
- [pnpm 10+](https://pnpm.io/installation) (the workspace uses pnpm 10 `catalog:`/overrides syntax)

---

## Setup

**Create a virtual environment (if required):**

- ```bash
  python -m venv .venv
  ```

**Activate venv:**

- PowerShell

  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```

- Bash

  ```bash
  source .venv/bin/activate
  ```

## API (Backend)

Set environment variables (while the virtual environment is active):

- PowerShell

  ```powershell
  # Replace <USER_HOME> with your user folder or path to the repos
  $env:AAZ_PATH = "<USER_HOME>/aaz"
  $env:AAZ_SWAGGER_PATH = "<USER_HOME>/azure-rest-api-specs"
  $env:AAZ_SWAGGER_MODULE_PATH = "<USER_HOME>/azure-rest-api-specs/specification"
  $env:AAZ_CLI_PATH = "<USER_HOME>/azure-cli"
  $env:AAZ_CLI_EXTENSION_PATH = "<USER_HOME>/azure-cli-extensions"

  $env:FLASK_APP="aaz_dev.app.app:create_app"
  ```

- Bash

  ```bash
  # Replace <USER_HOME> with your user folder or path to the repos
  export AAZ_PATH="<USER_HOME>/aaz"
  export AAZ_SWAGGER_PATH="<USER_HOME>/azure-rest-api-specs"
  export AAZ_SWAGGER_MODULE_PATH="<USER_HOME>/azure-rest-api-specs/specification"
  export AAZ_CLI_PATH="<USER_HOME>/azure-cli"
  export AAZ_CLI_EXTENSION_PATH="<USER_HOME>/azure-cli-extensions"

  export FLASK_APP="aaz_dev.app.app:create_app"
  ```

**Start application:**

- ```
  flask run --reload --port 5000
  ```

## Frontend:

- Install dependencies

  ```
  pnpm install
  pnpm build:typespec
  pnpm build:web
  pnpm run bundle


  cd src/web
  pnpm install
  ```

- Run front-end dev server (from `src/web`)

  ```
  pnpm run dev
  ```
