/**
 * Theme constants and colors.
 */

export const COLORS = {
  // Primary colors
  PRIMARY: '#2D5016',      // Dark green
  PRIMARY_LIGHT: '#4A7C2A',
  PRIMARY_DARK: '#1A3009',
  
  // Secondary colors
  SECONDARY: '#6B8E23',
  SECONDARY_LIGHT: '#9ACD32',
  SECONDARY_DARK: '#556B2F',
  
  // Neutral colors
  WHITE: '#FFFFFF',
  BLACK: '#000000',
  GRAY_LIGHT: '#F5F5F5',
  GRAY: '#CCCCCC',
  GRAY_DARK: '#666666',
  
  // Status colors
  SUCCESS: '#28A745',
  ERROR: '#DC3545',
  WARNING: '#FFC107',
  INFO: '#17A2B8',
  
  // Text colors
  TEXT_PRIMARY: '#212529',
  TEXT_SECONDARY: '#6C757D',
  TEXT_LIGHT: '#FFFFFF',
  
  // Background colors
  BG_PRIMARY: '#FFFFFF',
  BG_SECONDARY: '#F8F9FA',
  BG_DARK: '#212529',
};

export const SPACING = {
  XS: 4,
  SM: 8,
  MD: 16,
  LG: 24,
  XL: 32,
  XXL: 48,
};

export const FONT_SIZES = {
  XS: 12,
  SM: 14,
  MD: 16,
  LG: 18,
  XL: 20,
  XXL: 24,
  TITLE: 28,
};

export const BORDER_RADIUS = {
  SM: 4,
  MD: 8,
  LG: 12,
  XL: 16,
  ROUND: 999,
};

export const SHADOWS = {
  SM: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.18,
    shadowRadius: 1.0,
    elevation: 1,
  },
  MD: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.23,
    shadowRadius: 2.62,
    elevation: 4,
  },
  LG: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.30,
    shadowRadius: 4.65,
    elevation: 8,
  },
};
