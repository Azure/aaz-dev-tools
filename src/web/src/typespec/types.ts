import {
    CompilerHost,
    // CompilerOptions,
    LinterDefinition,
    PackageJson,
    TypeSpecLibrary,
} from "@typespec/compiler";

export interface TspLibrary {
    name: string;
    packageJson: PackageJson;
    isEmitter: boolean;
    definition?: TypeSpecLibrary<any>;
    linter?: LinterDefinition;
}

export interface BrowserHost extends CompilerHost {
    compiler: typeof import("@typespec/compiler");
    libraries: Record<string, TspLibrary>;
}
