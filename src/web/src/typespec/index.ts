import { createBrowserHost } from "./brower-host";
import { BrowserHost } from "./types";
import axios from "axios";

const libs = [
  "@typespec/compiler",
  "@typespec/events",
  "@typespec/http",
  "@typespec/rest",
  "@typespec/openapi",
  "@typespec/versioning",
  "@typespec/openapi3",
  "@typespec/json-schema",
  "@typespec/protobuf",
  "@typespec/sse",
  "@typespec/streams",
  "@typespec/xml",
  "@azure-tools/typespec-autorest",
  "@azure-tools/typespec-azure-core",
  "@azure-tools/typespec-client-generator-core",
  "@azure-tools/typespec-azure-resource-manager",
  "@azure-tools/typespec-aaz",
  "@azure-tools/typespec-liftr-base",
];

const outputDir = "tsp-output";

export async function getTypespecRPResources(resourceProviderUrl: string) {
  const host = await createBrowserHost(libs, { useShim: true });
  const res = await axios.get(resourceProviderUrl);
  const entryFiles = res.data.entryFiles;
  let results: any[] = [];
  for (const entryFile of entryFiles) {
    // cache entry files
    await host.stat(entryFile);
    await host.compiler.compile(host, entryFile, {
      outputDir: outputDir,
      emit: ["@azure-tools/typespec-aaz"],
      options: {
        "@azure-tools/typespec-aaz": {
          operation: "list-resources",
        },
      },
      trace: ["@azure-tools/typespec-aaz"],
    });

    const files = await findOutputFiles(host);
    const file = await host.readFile(outputDir + files[0]);
    results = [...results, ...JSON.parse(file.text)];
  }
  // exclude "/providers/[\w.]+/operations" id in results
  results = results.filter((it: any) => !it.id.match(/^\/providers\/[\w.]+\/operations$/g));
  return results;
}

async function findOutputFiles(host: BrowserHost): Promise<string[]> {
  const files: string[] = [];

  async function addFiles(dir: string) {
    const items = await host.readDir(outputDir + dir);
    for (const item of items) {
      const itemPath = `${dir}/${item}`;
      if ((await host.stat(outputDir + itemPath)).isDirectory()) {
        await addFiles(itemPath);
      } else {
        files.push(dir === "" ? item : `${dir}/${item}`);
      }
    }
  }
  await addFiles("");
  return files;
}

export async function getTypespecRPResourcesOperations(obj: any) {
  const host = await createBrowserHost(libs, { useShim: true });
  const res = await axios.get(obj.resourceProviderUrl);
  const entryFiles = res.data.entryFiles;
  for (const entryFile of entryFiles) {
    // cache entry files
    await host.stat(entryFile);
    const cfg = {
      outputDir: outputDir,
      emit: ["@azure-tools/typespec-aaz"],
      options: {
        "@azure-tools/typespec-aaz": {
          "operation": "get-resources-operations",
          "api-version": obj.version,
          "resources": obj.resources.map((it: any) => {
            return it.id;
          }),
        },
      },
      trace: ["@azure-tools/typespec-aaz"],
    };
    console.log(cfg);
    await host.compiler.compile(host, entryFile, cfg);

    const files = await findOutputFiles(host);
    const file = await host.readFile(outputDir + files[0]);
    return JSON.parse(file.text);
  }
}
