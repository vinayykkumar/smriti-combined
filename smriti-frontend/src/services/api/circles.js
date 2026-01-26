/**
 * Circles API Service
 * Handles all API calls for the Sangha Circles feature
 */
import { apiGet, apiPost, apiPut, apiDelete } from './client';

const CIRCLES_ENDPOINT = '/circles';

/**
 * Get all circles the current user is a member of
 * @returns {Promise<Array>} List of circles
 */
export const getCircles = async () => {
  const response = await apiGet(CIRCLES_ENDPOINT);
  return response.data?.circles || [];
};

/**
 * Get details of a specific circle
 * @param {string} circleId - Circle ID
 * @returns {Promise<Object>} Circle details
 */
export const getCircleDetails = async (circleId) => {
  const response = await apiGet(`${CIRCLES_ENDPOINT}/${circleId}`);
  return response.data?.circle || null;
};

/**
 * Create a new circle
 * @param {Object} data - Circle data
 * @param {string} data.name - Circle name (required)
 * @param {string} data.description - Circle description (optional)
 * @returns {Promise<Object>} Created circle with invite_code
 */
export const createCircle = async (data) => {
  const response = await apiPost(CIRCLES_ENDPOINT, data);
  return response.data?.circle || null;
};

/**
 * Update circle details (name/description)
 * @param {string} circleId - Circle ID
 * @param {Object} data - Update data
 * @returns {Promise<Object>} Updated circle
 */
export const updateCircle = async (circleId, data) => {
  const response = await apiPut(`${CIRCLES_ENDPOINT}/${circleId}`, data);
  return response.data?.circle || null;
};

/**
 * Preview a circle by invite code (before joining)
 * @param {string} inviteCode - 8-character invite code
 * @returns {Promise<Object>} Circle preview (name, member count)
 */
export const previewCircle = async (inviteCode) => {
  const response = await apiGet(`${CIRCLES_ENDPOINT}/preview/${inviteCode}`);
  return response.data || null;
};

/**
 * Join a circle using invite code
 * @param {string} inviteCode - 8-character invite code
 * @returns {Promise<Object>} Joined circle details
 */
export const joinCircle = async (inviteCode) => {
  const response = await apiPost(`${CIRCLES_ENDPOINT}/join/${inviteCode}`);
  return response.data?.circle || null;
};

/**
 * Regenerate invite code for a circle
 * @param {string} circleId - Circle ID
 * @returns {Promise<string>} New invite code
 */
export const regenerateInviteCode = async (circleId) => {
  const response = await apiPost(`${CIRCLES_ENDPOINT}/${circleId}/regenerate-invite`);
  return response.data?.invite_code || null;
};

/**
 * Get posts from a specific circle
 * @param {string} circleId - Circle ID
 * @param {number} skip - Number of posts to skip (pagination)
 * @param {number} limit - Max posts to return
 * @returns {Promise<Object>} { posts, total }
 */
export const getCirclePosts = async (circleId, skip = 0, limit = 20) => {
  const response = await apiGet(`${CIRCLES_ENDPOINT}/${circleId}/posts`, { skip, limit });
  return {
    posts: response.data?.posts || [],
    total: response.data?.total || 0
  };
};

/**
 * Vote to delete a circle (requires unanimous vote)
 * @param {string} circleId - Circle ID
 * @returns {Promise<Object>} Updated deletion status
 */
export const voteToDeleteCircle = async (circleId) => {
  const response = await apiPost(`${CIRCLES_ENDPOINT}/${circleId}/vote-delete`);
  return response.data || null;
};

/**
 * Revoke your vote to delete a circle
 * @param {string} circleId - Circle ID
 * @returns {Promise<Object>} Updated deletion status
 */
export const revokeDeleteVote = async (circleId) => {
  const response = await apiDelete(`${CIRCLES_ENDPOINT}/${circleId}/vote-delete`);
  return response.data || null;
};

export default {
  getCircles,
  getCircleDetails,
  createCircle,
  updateCircle,
  previewCircle,
  joinCircle,
  regenerateInviteCode,
  getCirclePosts,
  voteToDeleteCircle,
  revokeDeleteVote
};
