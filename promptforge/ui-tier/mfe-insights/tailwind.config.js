/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{ts,tsx}', './public/index.html'],
  theme: {
    extend: {
      colors: {
        primary: '#FF385C',
        'primary-hover': '#E31C5F',
        neutral: '#222222',
        success: '#00A699',
        warning: '#FFCC00',
        error: '#FF5A5F',
      },
    },
  },
  plugins: [],
}
