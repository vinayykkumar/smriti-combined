export const COLORS = {
  // Spiritual, calming palette (Warm Paper Aesthetic)
  background: '#EBE0D5',      // Warm Beige / Paper
  card: '#F5EEE6',            // Lighter Beige
  primary: '#4E342E',         // Dark Brown
  secondary: '#795548',       // Medium Brown
  accent: '#8D6E63',          // Avatar Brown
  text: '#4E342E',            // Dark Brown
  textLight: '#795548',       // Medium Brown
  border: '#D7CCC8',
  white: '#FFFFFF',
  success: '#6B8E23',
  error: '#C14A39',
  shadow: 'rgba(78, 52, 46, 0.1)',
};

// Profile Specific Theme (Warm/Beige)
export const PROFILE_COLORS = {
  background: '#EBE0D5',
  card: '#F5EEE6',
  textPrimary: '#4E342E',
  textSecondary: '#795548',
  accent: '#8D6E63',
  divider: '#D7CCC8',
  icon: '#5D4037',
  white: '#FFFFFF',
  shadow: 'rgba(78, 52, 46, 0.1)',
};

export const SPACING = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};

export const TYPOGRAPHY = {
  title: {
    fontSize: 28,
    fontWeight: '600',
    color: COLORS.text,
  },
  heading: {
    fontSize: 20,
    fontWeight: '600',
    color: COLORS.text,
  },
  body: {
    fontSize: 16,
    color: COLORS.text,
  },
  caption: {
    fontSize: 14,
    color: COLORS.textLight,
  },
};

export const SHADOWS = {
  small: {
    shadowColor: COLORS.shadow,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  medium: {
    shadowColor: COLORS.shadow,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 4,
  },
};
