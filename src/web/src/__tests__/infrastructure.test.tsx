import { describe, it, expect } from "vitest";
import { screen } from "@testing-library/react";
import { render } from "./test-utils";

// Simple component for testing infrastructure
function TestComponent() {
  return <div>Hello Testing World!</div>;
}

describe("Testing Infrastructure", () => {
  it("should render a simple component", () => {
    render(<TestComponent />);
    expect(screen.getByText("Hello Testing World!")).toBeInTheDocument();
  });

  it("should work with async operations", async () => {
    render(<TestComponent />);
    const element = await screen.findByText("Hello Testing World!");
    expect(element).toBeInTheDocument();
  });
});
