import React, { ReactElement } from "react";
import { render, RenderOptions } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { ThemeProvider } from "@mui/material/styles";
import theme from "../theme";

// Custom render function that includes all providers
function customRender(ui: ReactElement, options?: Omit<RenderOptions, "wrapper">) {
  function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <BrowserRouter>
        <ThemeProvider theme={theme}>{children}</ThemeProvider>
      </BrowserRouter>
    );
  }

  return render(ui, { wrapper: Wrapper, ...options });
}

// Re-export everything from RTL
export * from "@testing-library/react";

// Override render method with our custom one
export { customRender as render };
