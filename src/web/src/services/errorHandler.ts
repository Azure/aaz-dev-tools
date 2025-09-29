export const apiErrorHandler = {
  getErrorMessage: (err: any): string => {
    if (err.response?.data?.message) {
      const data = err.response.data;
      const details = data.details ? `: ${JSON.stringify(data.details)}` : "";
      return `ResponseError: ${data.message}${details}`;
    }
    return "An unexpected error occurred";
  },

  isHttpError: (err: any, statusCode: number): boolean => {
    return err.response?.status === statusCode;
  },
} as const;
