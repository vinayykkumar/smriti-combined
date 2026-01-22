/**
 * Tests for Card component.
 */
import React from 'react';
import { render } from '@testing-library/react-native';
import Card from '../../src/components/common/Card';

describe('Card Component', () => {
  it('renders correctly', () => {
    const { getByText } = render(<Card>Test Content</Card>);
    expect(getByText('Test Content')).toBeTruthy();
  });
});
