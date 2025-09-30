import "@testing-library/jest-dom";
import { beforeAll, afterEach, afterAll } from "vitest";
import { server } from "./__tests__/mocks/server.js";
import axios from "axios";

beforeAll(() => {
  axios.defaults.baseURL = "http://localhost:3000";

  server.listen({
    onUnhandledRequest: "bypass",
  });
});

afterEach(() => {
  server.resetHandlers();
});

afterAll(() => {
  server.close();
});
