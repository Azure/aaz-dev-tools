import { describe, it, expect } from "vitest";
import { errorHandlerApi } from "../services/errorHandlerApi";

describe("errorHandlerApi", () => {
  describe("getErrorMessage", () => {
    it("should extract message from axios response error with details", () => {
      const axiosError = {
        response: {
          data: {
            message: "Validation failed",
            details: { field: "name", reason: "required" },
          },
        },
      };

      const result = errorHandlerApi.getErrorMessage(axiosError);

      expect(result).toBe('ResponseError: Validation failed: {"field":"name","reason":"required"}');
    });

    it("should extract message from axios response error without details", () => {
      const axiosError = {
        response: {
          data: {
            message: "Server internal error",
          },
        },
      };

      const result = errorHandlerApi.getErrorMessage(axiosError);

      expect(result).toBe("ResponseError: Server internal error");
    });

    it("should handle standard Error objects", () => {
      const standardError = new Error("Network connection failed");

      const result = errorHandlerApi.getErrorMessage(standardError);

      expect(result).toBe("Network connection failed");
    });

    it("should handle plain objects with message property", () => {
      const plainError = {
        message: "Custom error message",
        code: "CUSTOM_ERROR",
      };

      const result = errorHandlerApi.getErrorMessage(plainError);

      expect(result).toBe("Custom error message");
    });

    it("should handle string errors", () => {
      const stringError = "Something went wrong";

      const result = errorHandlerApi.getErrorMessage(stringError);

      expect(result).toBe("Something went wrong");
    });

    it("should return default message for unknown error types", () => {
      const unknownError = { someProperty: "value" };

      const result = errorHandlerApi.getErrorMessage(unknownError);

      expect(result).toBe("An unexpected error occurred");
    });

    it("should return default message for null/undefined", () => {
      expect(errorHandlerApi.getErrorMessage(null)).toBe("An unexpected error occurred");
      expect(errorHandlerApi.getErrorMessage(undefined)).toBe("An unexpected error occurred");
    });

    it("should handle empty axios response data", () => {
      const emptyAxiosError = {
        response: {
          data: {},
        },
      };

      const result = errorHandlerApi.getErrorMessage(emptyAxiosError);

      expect(result).toBe("An unexpected error occurred");
    });
  });

  describe("isHttpError", () => {
    it("should return true for matching HTTP status code", () => {
      const httpError = {
        response: {
          status: 404,
          data: { message: "Not found" },
        },
      };

      const result = errorHandlerApi.isHttpError(httpError, 404);

      expect(result).toBe(true);
    });

    it("should return false for non-matching HTTP status code", () => {
      const httpError = {
        response: {
          status: 500,
          data: { message: "Server error" },
        },
      };

      const result = errorHandlerApi.isHttpError(httpError, 404);

      expect(result).toBe(false);
    });

    it("should return false for errors without response", () => {
      const nonHttpError = new Error("Network error");

      const result = errorHandlerApi.isHttpError(nonHttpError, 404);

      expect(result).toBe(false);
    });

    it("should return false for errors without status", () => {
      const errorWithoutStatus = {
        response: {
          data: { message: "Some error" },
        },
      };

      const result = errorHandlerApi.isHttpError(errorWithoutStatus, 404);

      expect(result).toBe(false);
    });

    it("should handle common HTTP status codes", () => {
      const error400 = { response: { status: 400 } };
      const error401 = { response: { status: 401 } };
      const error403 = { response: { status: 403 } };
      const error500 = { response: { status: 500 } };

      expect(errorHandlerApi.isHttpError(error400, 400)).toBe(true);
      expect(errorHandlerApi.isHttpError(error401, 401)).toBe(true);
      expect(errorHandlerApi.isHttpError(error403, 403)).toBe(true);
      expect(errorHandlerApi.isHttpError(error500, 500)).toBe(true);

      // Cross-check they don't match wrong codes
      expect(errorHandlerApi.isHttpError(error400, 401)).toBe(false);
      expect(errorHandlerApi.isHttpError(error500, 404)).toBe(false);
    });
  });
});
