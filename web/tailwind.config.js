/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f4f5fd',
          100: '#eef0fb',
          200: '#d9ddf7',
          300: '#b8bef0',
          400: '#9097e6',
          500: '#6c72dc',
          600: '#5b50e5', // Core accent from Host Node design
          700: '#4e40cf',
          800: '#4236a9',
          900: '#383086',
        },
        surface: {
          50: '#f8f9fc',
          100: '#f4f6fa',
          200: '#e9edf5',
          300: '#dce2ee',
        }
      },
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.5rem',
        '4xl': '2rem',
      },
      boxShadow: {
        'soft': '0 2px 15px -3px rgba(0, 0, 0, 0.04), 0 4px 6px -2px rgba(0, 0, 0, 0.02)',
        'soft-lg': '0 10px 25px -3px rgba(91, 80, 229, 0.06), 0 4px 6px -2px rgba(0, 0, 0, 0.03)',
        'card': '0 0 0 1px rgba(226, 232, 240, 0.8), 0 2px 4px rgba(0, 0, 0, 0.02)',
      }
    },
  },
  plugins: [],
}
