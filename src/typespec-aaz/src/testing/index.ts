import {
  createTestLibrary,
  findTestPackageRoot,
  TypeSpecTestLibrary,
} from "@typespec/compiler/testing";

export const TypespecAazTestLibrary: TypeSpecTestLibrary = createTestLibrary({
  name: "@azure-tools/typespec-aaz",
  packageRoot: await findTestPackageRoot(import.meta.url),
});
