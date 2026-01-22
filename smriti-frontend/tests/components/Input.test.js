/**
 * Tests for Input component.
 */
import React from 'react';
import { render } from '@testing-library/react-native';
import Input from '../../src/components/common/Input';

describe('Input Component', () => {
  it('renders correctly', () => {
    const { getByPlaceholderText } = render(
      <Input placeholder="Enter text" />
    );
    expect(getByPlaceholderText('Enter text')).toBeTruthy();
  });
});
