import "@testing-library/jest-dom";
import { beforeAll, afterEach, afterAll } from "vitest";
import { server } from "./__tests__/mocks/server.js";
import axios from "axios";

beforeAll(() => {
  // Set axios base URL for tests
  axios.defaults.baseURL = "http://localhost:3000";
  
  // Start MSW server
  server.listen({ 
    onUnhandledRequest: "bypass"
  });
});

afterEach(() => {
  // Reset any request handlers that are declared as a part of our tests
  server.resetHandlers();
});

afterAll(() => {
  // Clean up once the tests are done
  server.close();
});
