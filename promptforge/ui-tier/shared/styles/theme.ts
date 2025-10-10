/**
 * PromptForge Design System Theme
 *
 * Airbnb-inspired design system with modern minimalism
 * WCAG 2.1 AAA compliant
 */

export const theme = {
  colors: {
    // Primary - Airbnb-inspired accent
    primary: {
      DEFAULT: '#FF385C',
      dark: '#E31C5F',
      light: '#FF5A7A',
      foreground: '#FFFFFF',
    },

    // Neutral palette
    neutral: {
      DEFAULT: '#222222',
      50: '#FAFAFA',
      100: '#F7F7F7',
      200: '#EEEEEE',
      300: '#DDDDDD',
      400: '#B0B0B0',
      500: '#717171',
      600: '#484848',
      700: '#222222',
      800: '#1A1A1A',
      900: '#0D0D0D',
    },

    // Semantic colors
    success: {
      DEFAULT: '#00A699',
      light: '#4DB8AD',
      dark: '#008489',
      foreground: '#FFFFFF',
    },
    warning: {
      DEFAULT: '#FFB400',
      light: '#FFC933',
      dark: '#E6A200',
      foreground: '#222222',
    },
    error: {
      DEFAULT: '#C13515',
      light: '#E64A19',
      dark: '#A12810',
      foreground: '#FFFFFF',
    },
    info: {
      DEFAULT: '#0066FF',
      light: '#3385FF',
      dark: '#0052CC',
      foreground: '#FFFFFF',
    },

    // Background colors
    background: {
      DEFAULT: '#FFFFFF',
      secondary: '#F7F7F7',
      tertiary: '#FAFAFA',
    },

    // Text colors
    text: {
      DEFAULT: '#222222',
      secondary: '#717171',
      muted: '#B0B0B0',
      inverse: '#FFFFFF',
    },

    // Border colors
    border: {
      DEFAULT: '#DDDDDD',
      light: '#EEEEEE',
      dark: '#B0B0B0',
    },
  },

  typography: {
    fontFamily: {
      primary: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      display: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      mono: '"JetBrains Mono", "Fira Code", "Consolas", monospace',
    },
    fontSize: {
      xs: '0.75rem',    // 12px
      sm: '0.875rem',   // 14px
      base: '1rem',     // 16px
      lg: '1.125rem',   // 18px
      xl: '1.25rem',    // 20px
      '2xl': '1.5rem',  // 24px
      '3xl': '1.875rem',// 30px
      '4xl': '2.25rem', // 36px
    },
    fontWeight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    lineHeight: {
      tight: 1.25,
      normal: 1.5,
      relaxed: 1.75,
    },
  },

  spacing: {
    0: '0',
    1: '0.25rem',   // 4px
    2: '0.5rem',    // 8px
    3: '0.75rem',   // 12px
    4: '1rem',      // 16px
    5: '1.25rem',   // 20px
    6: '1.5rem',    // 24px
    8: '2rem',      // 32px
    10: '2.5rem',   // 40px
    12: '3rem',     // 48px
    16: '4rem',     // 64px
    20: '5rem',     // 80px
    24: '6rem',     // 96px
  },

  shadows: {
    none: 'none',
    sm: '0 1px 2px rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px rgba(0, 0, 0, 0.1)',
    lg: '0 10px 15px rgba(0, 0, 0, 0.1)',
    xl: '0 20px 25px rgba(0, 0, 0, 0.1)',
    '2xl': '0 25px 50px rgba(0, 0, 0, 0.15)',
  },

  borderRadius: {
    none: '0',
    sm: '0.25rem',  // 4px
    md: '0.5rem',   // 8px
    lg: '0.75rem',  // 12px
    xl: '1rem',     // 16px
    '2xl': '1.5rem',// 24px
    full: '9999px',
  },

  transitions: {
    duration: {
      fast: '150ms',
      normal: '200ms',
      slow: '300ms',
    },
    timing: {
      ease: 'ease',
      easeIn: 'ease-in',
      easeOut: 'ease-out',
      easeInOut: 'ease-in-out',
    },
  },

  // Component-specific tokens
  components: {
    button: {
      height: {
        sm: '2rem',    // 32px
        md: '2.5rem',  // 40px
        lg: '3rem',    // 48px
      },
      padding: {
        sm: '0.5rem 0.75rem',    // 8px 12px
        md: '0.625rem 1rem',     // 10px 16px
        lg: '0.75rem 1.5rem',    // 12px 24px
      },
      minWidth: '2.75rem',       // 44px - minimum touch target
    },
    input: {
      height: {
        sm: '2rem',    // 32px
        md: '2.5rem',  // 40px
        lg: '3rem',    // 48px
      },
      padding: {
        sm: '0.375rem 0.75rem',  // 6px 12px
        md: '0.5rem 0.875rem',   // 8px 14px
        lg: '0.625rem 1rem',     // 10px 16px
      },
    },
    card: {
      padding: {
        sm: '1rem',     // 16px
        md: '1.5rem',   // 24px
        lg: '2rem',     // 32px
      },
    },
  },

  // Accessibility
  accessibility: {
    focusRing: '0 0 0 3px rgba(255, 56, 92, 0.2)',
    minTouchTarget: '44px',
    contrastRatios: {
      normalText: 7,      // AAA standard
      largeText: 4.5,     // AAA standard
    },
  },
} as const;

export type Theme = typeof theme;

// Tailwind configuration helper
export const tailwindTheme = {
  colors: {
    primary: theme.colors.primary,
    neutral: theme.colors.neutral,
    success: theme.colors.success,
    warning: theme.colors.warning,
    error: theme.colors.error,
    info: theme.colors.info,
    background: theme.colors.background,
    text: theme.colors.text,
    border: theme.colors.border,
  },
  fontFamily: {
    sans: theme.typography.fontFamily.primary.split(','),
    mono: theme.typography.fontFamily.mono.split(','),
  },
  fontSize: theme.typography.fontSize,
  fontWeight: theme.typography.fontWeight,
  spacing: theme.spacing,
  borderRadius: theme.borderRadius,
  boxShadow: theme.shadows,
  transitionDuration: theme.transitions.duration,
  transitionTimingFunction: theme.transitions.timing,
};

export default theme;
