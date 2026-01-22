/**
 * Tests for API service.
 */
import { API_BASE_URL } from '../../src/constants/config';

describe('API Service', () => {
  it('has correct base URL configured', () => {
    expect(API_BASE_URL).toBeDefined();
  });

  // Add more API tests as needed
});
