/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        base:    "#08060E",
        surface: "#0D0B16",
        border:  "#1C1628",
        primary:   "#FE7235",
        secondary: "#FEA735",
        cyan:    "#00C3FF",
        azure:   "#0077FF",
        linen:   "#FCF5EF",
        muted:   "#4A3D5A",
        hint:    "#3D3050",
        dim:     "#2A2040",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      borderRadius: {
        DEFAULT: "8px",
        lg: "12px",
        xl: "16px",
        "2xl": "20px",
      },
    },
  },
  plugins: [],
};
