# FAQ
---

## 1. Why drop autorest framework in AAZ-Dev Tool?
---
1. It helps to generate Atomic Commands without relies on SDKs. Atomic commands can help to reduce the package size and save the efforts to bump up SDKs.
2. AAZ-Dev separates the generation in two steps: 1. swagger to command model. 2. command model to code. It's more flexible than Autorest which generates code directly from swagger. With this flexibility, we implement multi api versions and multi profiles support.
3. Autorest uses configuration files to support modifications. However, it's hard to learn and not easy to use for beginners. AAZDev tool use declarative command model, the modification of it is state-of-truth, and we provide an easy-to-use portal for users.

## 2. Does AAZDev support data-plane APIs?
---
Not Yet. Currently the AAZDev tool is focus on Management-plane APIs. However, the framework of AAZDev is designed to support Data-plane APIs. As we know data-plane APIs are much different cross resource providers. So we plane to support them case by case.

## 3. Filename too long in Git for Windows
---
The path of configuration files in aaz repo will have more than 260 characters. It will cause a `Filename too long` issue while using `git`.
Please enable the `core.longpaths` module by the following command in terminal which is in `Run as administrator` mode.
```bash
git config --system core.longpaths true
```
