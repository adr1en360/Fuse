/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        fuse: {
          cyan: "#74cfd8",
          dark: "#05080e",
          light: "#fefefe",
          cyanHover: "#5bbec8",
        },
        tremor: {
          brand: {
            faint: "#eff6ff",
            muted: "#bfdbfe",
            subtle: "#60a5fa",
            DEFAULT: "#3b82f6",
            emphasis: "#1d4ed8",
            inverted: "#ffffff",
          },
          background: {
            muted: "#f9fafb",
            subtle: "#f3f4f6",
            DEFAULT: "#ffffff",
            emphasis: "#374151",
          },
          border: {
            DEFAULT: "#e5e7eb",
          },
          ring: {
            DEFAULT: "#e5e7eb",
          },
          content: {
            subtle: "#9ca3af",
            DEFAULT: "#6b7280",
            emphasis: "#374151",
            strong: "#111827",
            inverted: "#ffffff",
          },
        },
        "dark-tremor": {
          brand: {
            faint: "#0B1229",
            muted: "#172554",
            subtle: "#1d4ed8",
            DEFAULT: "#3b82f6",
            emphasis: "#60a5fa",
            inverted: "#030712",
          },
          background: {
            muted: "#131A2B",
            subtle: "#1f2937",
            DEFAULT: "#0b0f19",
            emphasis: "#d1d5db",
          },
          border: {
            DEFAULT: "#1f293d",
          },
          ring: {
            DEFAULT: "#1f293d",
          },
          content: {
            subtle: "#4b5563",
            DEFAULT: "#94a3b8",
            emphasis: "#e2e8f0",
            strong: "#f8fafc",
            inverted: "#000000",
          },
        },
      },
    },
  },
  plugins: [],
}
