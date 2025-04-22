import { Diagnostic, resolvePath } from "@typespec/compiler";
import { TestHost, createTestHost, createTestWrapper, BasicTestRunner } from "@typespec/compiler/testing";
import { HttpTestLibrary } from "@typespec/http/testing";
import { OpenAPITestLibrary } from "@typespec/openapi/testing";
import { RestTestLibrary } from "@typespec/rest/testing";
import { VersioningTestLibrary } from "@typespec/versioning/testing";
import { AzureCoreTestLibrary } from "@azure-tools/typespec-azure-core/testing";
import { AzureResourceManagerTestLibrary } from "@azure-tools/typespec-azure-resource-manager/testing";
import { TypespecAazTestLibrary } from "../src/testing/index.js";
import { AAZEmitterOptions } from "../src/lib.js";

export async function createTypespecAazTestHost() {
  return createTestHost({
    libraries: [
      HttpTestLibrary,
      RestTestLibrary,
      VersioningTestLibrary,
      OpenAPITestLibrary,
      AzureCoreTestLibrary,
      AzureResourceManagerTestLibrary,
      TypespecAazTestLibrary,
    ],
  });
}

export async function createTypespecAazTestRunner(host?: TestHost) {
  host ??= await createTypespecAazTestHost();

  return createTestWrapper(host, {
    autoUsings: [
      "TypeSpec.Http",
      "TypeSpec.Rest",
      "TypeSpec.Versioning",
      "TypeSpec.OpenAPI",
      "Azure.Core",
      "Azure.ResourceManager",
    ],
    compilerOptions: {
      emit: ["@azure-tools/typespec-aaz"],
    },
  });
}

export async function emitWithDiagnostics(
  code: string,
  options: AAZEmitterOptions,
  runner?: BasicTestRunner,
): Promise<[string | undefined, readonly Diagnostic[]]> {
  runner ??= await createTypespecAazTestRunner();
  const emitterOutputDir = "./tsp-output/@azure-tools/typespec-aaz";
  await runner.compileAndDiagnose(code, {
    emit: ["@azure-tools/typespec-autorest"],
    options: {
      "@azure-tools/typespec-aaz": { ...options },
    },
    outputDir: "tsp-output",
  });
  const files = await runner.program.host.readDir(emitterOutputDir);

  const result: Record<string, string> = {};
  for (const file of files) {
    result[file] = (await runner.program.host.readFile(resolvePath(emitterOutputDir, file))).text;
  }
  if (options.operation === "list-resources") {
    return [result["resources.json"], runner.program.diagnostics];
  } else if (options.operation === "get-resources-operations") {
    return [result["resources_operations.json"], runner.program.diagnostics];
  } else {
    return [undefined, runner.program.diagnostics];
  }
}

export async function compileTypespecAAZOperations(
  code: string,
  options: AAZEmitterOptions,
  runner?: BasicTestRunner,
): Promise<string | undefined> {
  runner ??= await createTypespecAazTestRunner();
  const emitterOutputDir = "./tsp-output/@azure-tools/typespec-aaz";
  await runner.compile(code, {
    noEmit: false,
    emit: ["@azure-tools/typespec-aaz"],
    options: {
      "@azure-tools/typespec-aaz": { ...options },
    },
    outputDir: "tsp-output",
  });
  const files = await runner.program.host.readDir(emitterOutputDir);
  const result: Record<string, string> = {};
  for (const file of files) {
    const fileContent = (await runner.program.host.readFile(resolvePath(emitterOutputDir, file))).text;
    result[file] = fileContent;
  }
  if (options.operation === "list-resources") {
    return result["resources.json"];
  } else if (options.operation === "get-resources-operations") {
    return result["resources_operations.json"];
  } else {
    return undefined;
  }
}
