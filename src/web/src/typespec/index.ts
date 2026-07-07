import { getSourceLocation } from "@typespec/compiler";
import { createBrowserHost, resolveVirtualPath } from "./brower-host";
import { BrowserHost } from "./types";
import axios from "axios";

// ponytail: dev-only aid — turn a bare diagnostic into file:line:col + source snippet
// so an "invalid-argument" cascade points at the exact spec/decorator that triggers it.
function describeTarget(target: any): string {
  try {
    const sl: any = getSourceLocation(target, { locateId: true } as any);
    const text: string = sl?.file?.text ?? "";
    if (!sl?.file || typeof sl.pos !== "number") return "";
    const before = text.slice(0, sl.pos);
    const lineNo = before.split("\n").length;
    const col = sl.pos - (before.lastIndexOf("\n") + 1) + 1;
    const path = sl.file.path ?? "?";
    const snippet = text.slice(sl.pos, Math.min(sl.end ?? sl.pos + 80, sl.pos + 80)).replace(/\n/g, "\\n");
    return `\n    @ ${path}:${lineNo}:${col}  «${snippet}»`;
  } catch {
    return "";
  }
}

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

// Emitters only run when compilation succeeds; on error `compile` returns before writing
// any output, leaving `findOutputFiles` empty. Surface the real diagnostics instead of the
// misleading "tsp-outputundefined not found" that comes from reading a missing output file.
export function assertCompiled(program: any, files: string[]) {
  const errors = (program?.diagnostics ?? []).filter((d: any) => d.severity === "error");
  if (files.length === 0 || errors.length > 0) {
    // Build the message from the diagnostic's own fields; the browser build's
    // `formatDiagnostic` JSON.stringifies the whole diagnostic and throws on the
    // circular `target.parent` node references.
    const details = errors
      .map((d: any) => `${d.code ? `${d.code}: ` : ""}${d.message}${describeTarget(d.target)}`)
      .join("\n");
    throw new Error(`TypeSpec compilation failed:\n${details || "no output produced"}`);
  }
}

export async function getTypespecRPResources(resourceProviderUrl: string) {
  const host = await createBrowserHost(libs, { useShim: true });
  const res = await axios.get(resourceProviderUrl);
  const entryFiles = res.data.entryFiles;
  let results: any[] = [];
  for (const entryFile of entryFiles) {
    // The backend returns a *relative* entry path (e.g. "specification/.../main.tsp"), but the
    // host's readFile rewrites every path to the absolute virtual path ("/aaz-host/..."). Compile
    // with the absolute path so the compiler's dedup key matches; otherwise a circular import
    // (main.tsp <-> client.tsp) re-imports main.tsp via its absolute path, misses the relative
    // seen-guard, and throws "Duplicate script path".
    const absEntryFile = resolveVirtualPath(entryFile);
    // cache entry files
    await host.stat(absEntryFile);
    const program = await host.compiler.compile(host, absEntryFile, {
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
    assertCompiled(program, files);
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
        files.push(`${dir}/${item}`);
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
    const absEntryFile = resolveVirtualPath(entryFile);
    // cache entry files
    await host.stat(absEntryFile);
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
    const program = await host.compiler.compile(host, absEntryFile, cfg);

    const files = await findOutputFiles(host);
    assertCompiled(program, files);
    const file = await host.readFile(outputDir + files[0]);
    return JSON.parse(file.text);
  }
}
