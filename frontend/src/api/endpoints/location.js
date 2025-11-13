import apiClient from '../client';

export const locationAPI = {
  /**
   * @param {string} query
   * @returns {Promise}
   */
  search: async (query) => {
    const { data } = await apiClient.post('/api/location/disambiguate', { 
      location: query 
    });
    return data;
  },
};