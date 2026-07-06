import { describe, it, expect } from "vitest";
import { assertCompiled } from "../../typespec";

describe("assertCompiled", () => {
  it("passes when output produced and no errors", () => {
    expect(() => assertCompiled({ diagnostics: [] }, ["/resources.json"])).not.toThrow();
  });

  it("throws real diagnostics (code + message) instead of tsp-outputundefined when no output", () => {
    expect(() =>
      assertCompiled(
        { diagnostics: [{ severity: "error", code: "missing-import", message: "cannot find lib", target: {} }] },
        [],
      ),
    ).toThrow(/missing-import: cannot find lib/);
  });

  it("does not throw on circular diagnostic targets", () => {
    const target: any = {};
    target.parent = target;
    expect(() =>
      assertCompiled({ diagnostics: [{ severity: "error", message: "boom", target }] }, []),
    ).toThrow(/boom/);
  });

  it("throws when output is empty even without diagnostics", () => {
    expect(() => assertCompiled({ diagnostics: [] }, [])).toThrow(/no output produced/);
  });
});
