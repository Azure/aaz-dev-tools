import { describe, it, expect } from "vitest";
import { convertArgDefaultText, type SupportedArgType } from "../../views/workspace/utils/convertArgDefaultText";

describe("convertArgDefaultText", () => {
  describe("String types", () => {
    const stringTypes: SupportedArgType[] = [
      "byte",
      "binary",
      "duration",
      "date",
      "dateTime",
      "time",
      "uuid",
      "password",
      "SubscriptionId",
      "ResourceGroupName",
      "ResourceId",
      "ResourceLocation",
      "string",
    ];

    stringTypes.forEach((type) => {
      it(`should convert valid ${type} values`, () => {
        expect(convertArgDefaultText("  hello world  ", type)).toBe("hello world");
        expect(convertArgDefaultText("test-value", type)).toBe("test-value");
      });

      it(`should throw error for empty ${type} values`, () => {
        expect(() => convertArgDefaultText("", type)).toThrow(`Not supported empty value: ''`);
        expect(() => convertArgDefaultText("   ", type)).toThrow(`Not supported empty value: '   '`);
      });
    });
  });

  describe("Integer types", () => {
    const integerTypes: SupportedArgType[] = ["integer32", "integer64", "integer"];

    integerTypes.forEach((type) => {
      it(`should convert valid ${type} values`, () => {
        expect(convertArgDefaultText("42", type)).toBe(42);
        expect(convertArgDefaultText("  123  ", type)).toBe(123);
        expect(convertArgDefaultText("-456", type)).toBe(-456);
        expect(convertArgDefaultText("0", type)).toBe(0);
      });

      it(`should throw error for invalid ${type} values`, () => {
        expect(() => convertArgDefaultText("abc", type)).toThrow(`Not supported default value for integer type: 'abc'`);
        expect(() => convertArgDefaultText("12.34", type)).toThrow(
          `Not supported default value for integer type: '12.34'`,
        );
        expect(() => convertArgDefaultText("", type)).toThrow(`Not supported default value for integer type: ''`);
      });
    });
  });

  describe("Float types", () => {
    const floatTypes: SupportedArgType[] = ["float32", "float64", "float"];

    floatTypes.forEach((type) => {
      it(`should convert valid ${type} values`, () => {
        expect(convertArgDefaultText("42.5", type)).toBe(42.5);
        expect(convertArgDefaultText("  123.456  ", type)).toBe(123.456);
        expect(convertArgDefaultText("-456.789", type)).toBe(-456.789);
        expect(convertArgDefaultText("0.0", type)).toBe(0.0);
        expect(convertArgDefaultText("42", type)).toBe(42);
      });

      it(`should throw error for invalid ${type} values`, () => {
        expect(() => convertArgDefaultText("abc", type)).toThrow(`Not supported default value for float type: 'abc'`);
        expect(() => convertArgDefaultText("", type)).toThrow(`Not supported default value for float type: ''`);
      });
    });
  });

  describe("Boolean type", () => {
    it("should convert true values", () => {
      expect(convertArgDefaultText("true", "boolean")).toBe(true);
      expect(convertArgDefaultText("TRUE", "boolean")).toBe(true);
      expect(convertArgDefaultText("  True  ", "boolean")).toBe(true);
      expect(convertArgDefaultText("yes", "boolean")).toBe(true);
      expect(convertArgDefaultText("YES", "boolean")).toBe(true);
    });

    it("should convert false values", () => {
      expect(convertArgDefaultText("false", "boolean")).toBe(false);
      expect(convertArgDefaultText("FALSE", "boolean")).toBe(false);
      expect(convertArgDefaultText("  False  ", "boolean")).toBe(false);
      expect(convertArgDefaultText("no", "boolean")).toBe(false);
      expect(convertArgDefaultText("NO", "boolean")).toBe(false);
    });

    it("should throw error for invalid boolean values", () => {
      expect(() => convertArgDefaultText("maybe", "boolean")).toThrow(
        `Not supported default value for boolean type: 'maybe'`,
      );
      expect(() => convertArgDefaultText("1", "boolean")).toThrow(`Not supported default value for boolean type: '1'`);
      expect(() => convertArgDefaultText("", "boolean")).toThrow(`Not supported default value for boolean type: ''`);
    });
  });

  describe("Any type", () => {
    it("should convert integer values", () => {
      expect(convertArgDefaultText("42", "any")).toBe(42);
      expect(convertArgDefaultText("-123", "any")).toBe(-123);
    });

    it("should convert float values", () => {
      expect(convertArgDefaultText("42.5", "any")).toBe(42.5);
      expect(convertArgDefaultText("-123.456", "any")).toBe(-123.456);
    });

    it("should convert null values", () => {
      expect(convertArgDefaultText("null", "any")).toBe(null);
      expect(convertArgDefaultText("NULL", "any")).toBe(null);
    });

    it("should convert boolean values", () => {
      expect(convertArgDefaultText("true", "any")).toBe(true);
      expect(convertArgDefaultText("false", "any")).toBe(false);
      expect(convertArgDefaultText("yes", "any")).toBe(true);
      expect(convertArgDefaultText("no", "any")).toBe(false);
    });

    it("should convert string values as fallback", () => {
      expect(convertArgDefaultText("hello", "any")).toBe("hello");
      expect(convertArgDefaultText("some text", "any")).toBe("some text");
    });
  });

  describe("Object type", () => {
    it("should parse valid JSON objects", () => {
      expect(convertArgDefaultText('{"key": "value"}', "object")).toEqual({ key: "value" });
      expect(convertArgDefaultText('{"number": 42, "boolean": true}', "object")).toEqual({ number: 42, boolean: true });
      expect(convertArgDefaultText('  {"nested": {"key": "value"}}  ', "object")).toEqual({ nested: { key: "value" } });
    });

    it("should throw error for invalid JSON", () => {
      expect(() => convertArgDefaultText("{invalid json}", "object")).toThrow();
      expect(() => convertArgDefaultText("not json at all", "object")).toThrow();
    });
  });

  describe("Array types", () => {
    it("should parse valid JSON arrays for array types", () => {
      expect(convertArgDefaultText("[1, 2, 3]", "array<integer>")).toEqual([1, 2, 3]);
      expect(convertArgDefaultText('["a", "b", "c"]', "array<string>")).toEqual(["a", "b", "c"]);
      expect(convertArgDefaultText("  []  ", "array<any>")).toEqual([]);
    });

    it("should throw error for invalid JSON arrays", () => {
      expect(() => convertArgDefaultText("[invalid, json]", "array<string>")).toThrow();
      expect(() => convertArgDefaultText("not an array", "array<integer>")).toThrow();
    });
  });

  describe("Dictionary types", () => {
    it("should parse valid JSON objects for dict types", () => {
      expect(convertArgDefaultText('{"key1": "value1"}', "dict<string>")).toEqual({ key1: "value1" });
      expect(convertArgDefaultText('{"a": 1, "b": 2}', "dict<integer>")).toEqual({ a: 1, b: 2 });
      expect(convertArgDefaultText("  {}  ", "dict<any>")).toEqual({});
    });

    it("should throw error for invalid JSON dictionaries", () => {
      expect(() => convertArgDefaultText("{invalid: json}", "dict<string>")).toThrow();
      expect(() => convertArgDefaultText("not a dict", "dict<any>")).toThrow();
    });
  });

  describe("Unsupported types", () => {
    it("should throw error for unsupported types", () => {
      expect(() => convertArgDefaultText("value", "unsupported")).toThrow("Not supported type: unsupported");
      expect(() => convertArgDefaultText("value", "custom-type")).toThrow("Not supported type: custom-type");
    });
  });

  describe("Edge cases", () => {
    it("should handle whitespace correctly", () => {
      expect(convertArgDefaultText("  value  ", "string")).toBe("value");
      expect(convertArgDefaultText("  42  ", "integer")).toBe(42);
      expect(convertArgDefaultText("  true  ", "boolean")).toBe(true);
    });

    it("should handle case sensitivity for any type", () => {
      expect(convertArgDefaultText("TRUE", "any")).toBe(true);
      expect(convertArgDefaultText("FALSE", "any")).toBe(false);
      expect(convertArgDefaultText("NULL", "any")).toBe(null);
    });
  });
});
