/**
 * Tests for Button component.
 */
import React from 'react';
import { render } from '@testing-library/react-native';
import Button from '../../src/components/common/Button';

describe('Button Component', () => {
  it('renders correctly', () => {
    const { getByText } = render(<Button title="Test Button" />);
    expect(getByText('Test Button')).toBeTruthy();
  });

  // Add more tests as needed
});
