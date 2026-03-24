import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import App from "./App";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: "#0D0B16",
            color: "#FCF5EF",
            border: "1px solid #1C1628",
            fontSize: "13px",
          },
          success: { iconTheme: { primary: "#FE7235", secondary: "#FCF5EF" } },
          error: { iconTheme: { primary: "#f87171", secondary: "#FCF5EF" } },
        }}
      />
    </BrowserRouter>
  </React.StrictMode>
);
