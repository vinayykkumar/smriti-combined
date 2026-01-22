/**
 * Permission and capability checking utilities.
 */

/**
 * Check if user has permission
 * @param {Array<string>} userPermissions - User's permissions
 * @param {string} requiredPermission - Required permission
 * @returns {boolean} - True if user has permission
 */
export const hasPermission = (userPermissions = [], requiredPermission) => {
  if (!userPermissions || !Array.isArray(userPermissions)) {
    return false;
  }
  return userPermissions.includes(requiredPermission);
};

/**
 * Check if user has any of the required permissions
 * @param {Array<string>} userPermissions - User's permissions
 * @param {Array<string>} requiredPermissions - Required permissions
 * @returns {boolean} - True if user has at least one permission
 */
export const hasAnyPermission = (userPermissions = [], requiredPermissions = []) => {
  if (!userPermissions || !Array.isArray(userPermissions)) {
    return false;
  }
  return requiredPermissions.some(permission => userPermissions.includes(permission));
};

/**
 * Check if user has all required permissions
 * @param {Array<string>} userPermissions - User's permissions
 * @param {Array<string>} requiredPermissions - Required permissions
 * @returns {boolean} - True if user has all permissions
 */
export const hasAllPermissions = (userPermissions = [], requiredPermissions = []) => {
  if (!userPermissions || !Array.isArray(userPermissions)) {
    return false;
  }
  return requiredPermissions.every(permission => userPermissions.includes(permission));
};

/**
 * Check if user is owner of resource
 * @param {string} userId - Current user ID
 * @param {string} resourceUserId - Resource owner ID
 * @returns {boolean} - True if user is owner
 */
export const isOwner = (userId, resourceUserId) => {
  return userId && resourceUserId && userId === resourceUserId;
};
