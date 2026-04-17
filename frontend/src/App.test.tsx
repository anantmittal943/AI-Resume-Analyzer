import { render, screen } from "@testing-library/react";

import App from "./App";


describe("App", () => {
  it("shows auth panel when user is not authenticated", () => {
    localStorage.clear();
    render(<App />);
    expect(screen.getByText("AI Resume Analyzer")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Register" })).toBeInTheDocument();
    expect(screen.getByLabelText("Email")).toBeInTheDocument();
  });
});
