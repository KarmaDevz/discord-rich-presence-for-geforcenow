/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    './pages/**/*.{js,jsx}',
    './components/**/*.{js,jsx}',
    './app/**/*.{js,jsx}',
    './src/**/*.{js,jsx}',
  ],
  prefix: "",
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "var(--color-border)", /* subtle white border */
        input: "var(--color-input)", /* elevated dark surface */
        ring: "var(--color-ring)", /* electric cyan */
        background: "var(--color-background)", /* near-black */
        foreground: "var(--color-foreground)", /* high-contrast white */
        primary: {
          DEFAULT: "var(--color-primary)", /* electric cyan */
          foreground: "var(--color-primary-foreground)", /* near-black */
        },
        secondary: {
          DEFAULT: "var(--color-secondary)", /* deep violet */
          foreground: "var(--color-secondary-foreground)", /* high-contrast white */
        },
        destructive: {
          DEFAULT: "var(--color-destructive)", /* clear red */
          foreground: "var(--color-destructive-foreground)", /* high-contrast white */
        },
        muted: {
          DEFAULT: "var(--color-muted)", /* very subtle white */
          foreground: "var(--color-muted-foreground)", /* muted gray */
        },
        accent: {
          DEFAULT: "var(--color-accent)", /* success green */
          foreground: "var(--color-accent-foreground)", /* high-contrast white */
        },
        popover: {
          DEFAULT: "var(--color-popover)", /* elevated dark surface */
          foreground: "var(--color-popover-foreground)", /* high-contrast white */
        },
        card: {
          DEFAULT: "var(--color-card)", /* elevated dark surface */
          foreground: "var(--color-card-foreground)", /* high-contrast white */
        },
        success: {
          DEFAULT: "var(--color-success)", /* bright green */
          foreground: "var(--color-success-foreground)", /* near-black */
        },
        warning: {
          DEFAULT: "var(--color-warning)", /* amber */
          foreground: "var(--color-warning-foreground)", /* near-black */
        },
        error: {
          DEFAULT: "var(--color-error)", /* clear red */
          foreground: "var(--color-error-foreground)", /* high-contrast white */
        },
        surface: "var(--color-surface)", /* elevated dark surface */
        'text-primary': "var(--color-text-primary)", /* high-contrast white */
        'text-secondary': "var(--color-text-secondary)", /* muted gray */
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      fontFamily: {
        'heading': ['Inter', 'sans-serif'],
        'body': ['Inter', 'sans-serif'],
        'mono': ['JetBrains Mono', 'monospace'],
      },
      fontWeight: {
        'heading-normal': '400',
        'heading-semibold': '600',
        'heading-bold': '700',
        'body-normal': '400',
        'body-medium': '500',
        'mono-normal': '400',
        'mono-medium': '500',
      },
      boxShadow: {
        'glow-primary': '0 4px 6px rgba(0, 217, 255, 0.1), 0 10px 15px rgba(0, 0, 0, 0.3)',
        'glow-primary-hover': '0 6px 12px rgba(0, 217, 255, 0.2), 0 15px 25px rgba(0, 0, 0, 0.4)',
        'glow-intense': '0 8px 16px rgba(0, 217, 255, 0.3), 0 20px 35px rgba(0, 0, 0, 0.5)',
      },
      animation: {
        'pulse-glow': 'pulse-glow 2s linear infinite',
      },
      keyframes: {
        'pulse-glow': {
          '0%, 100%': { 
            boxShadow: '0 6px 12px rgba(0, 217, 255, 0.2), 0 15px 25px rgba(0, 0, 0, 0.4)' 
          },
          '50%': { 
            boxShadow: '0 8px 16px rgba(0, 217, 255, 0.3), 0 20px 35px rgba(0, 0, 0, 0.5)' 
          },
        },
      },
      backdropBlur: {
        'glass': '10px',
      },
      transitionTimingFunction: {
        'micro': 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
      },
      transitionDuration: {
        'micro': '150ms',
        'content': '300ms',
      },
    },
  },
  plugins: [
    require("tailwindcss-animate"),
  ],
}