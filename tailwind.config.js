/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './app/templates/**/*.html',
    './app/static/src/**/*.css',
    './app/static/js/**/*.js',
    './node_modules/flowbite/**/*.js'
  ],
  theme: {
    extend: {
      animation: {
        fade: 'fadeIn .5s ease-in-out',
      },
      keyframes: {
        fadeIn: {
          from: { opacity: 0 },
          to: { opacity: 1 },
        }
      }
    }
  },
  plugins: [
    require('flowbite/plugin')
  ],
};
