/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        brand: {
          50:  "#eeedfe",
          100: "#cecbf6",
          400: "#7f77dd",
          600: "#534ab7",
          900: "#26215c",
        },
        surface: {
          900: "#0f0e17",
          800: "#16141f",
          700: "#1e1c2a",
          600: "#272535",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
    },
  },
  plugins: [],
};
