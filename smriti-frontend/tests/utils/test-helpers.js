/**
 * Test helper utilities.
 */

export const createMockUser = () => ({
  userId: 'test-user-id',
  username: 'testuser',
  email: 'test@example.com',
  token: 'mock-token',
});

export const createMockPost = () => ({
  _id: 'test-post-id',
  contentType: 'note',
  title: 'Test Post',
  textContent: 'This is a test post',
  author: {
    username: 'testuser',
    userId: 'test-user-id',
  },
  createdAt: new Date().toISOString(),
});

export const waitFor = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
