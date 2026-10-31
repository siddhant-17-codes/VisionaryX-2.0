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
        muted:   "#A495B7",  // 7.0:1 on base and surface (WCAG AA body text)
        hint:    "#947FB2",  // 5.5:1
        dim:     "#856FB7",  // 4.6:1, the lowest that still passes AA
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
