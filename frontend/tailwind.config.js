export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          50: '#f9fafb',
          100: '#f3f4f6',
          900: '#0f172a',
          950: '#030712',
        },
        brand: {
          primary: '#6C63FF',
          secondary: '#00D4FF',
          accent: '#FF6B9D',
        }
      },
      fontFamily: {
        inter: ['Inter', 'sans-serif'],
      },
      backdropBlur: {
        xs: '2px',
        sm: '4px',
        md: '8px',
        lg: '12px',
        xl: '16px',
      }
    },
  },
  plugins: [],
}
