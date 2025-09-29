export const apiErrorHandler = {
  getErrorMessage: (err: any): string => {
    console.log("err: ", err);

    if (err.response?.data?.message) {
      const data = err.response.data;
      const details = data.details ? `: ${JSON.stringify(data.details)}` : "";
      return `ResponseError: ${data.message}${details}`;
    }

    if (err instanceof Error && err.message) {
      return err.message;
    }

    if (err && typeof err === "object" && err.message) {
      return err.message;
    }

    if (typeof err === "string") {
      return err;
    }

    return "An unexpected error occurred";
  },

  isHttpError: (err: any, statusCode: number): boolean => {
    return err.response?.status === statusCode;
  },
} as const;
