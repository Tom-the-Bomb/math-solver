const defaultTheme = require('tailwindcss/defaultTheme')

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'math': ['Noto_Serif', ...defaultTheme.fontFamily.serif],
        'mono': ['Jetbrains_Mono', ...defaultTheme.fontFamily.mono],
      },
      colors: {
        'red-1': 'rgb(190, 28, 85)',
        'red-2': 'rgb(215, 20, 40)'
      }
    },
  },
  plugins: [],
}