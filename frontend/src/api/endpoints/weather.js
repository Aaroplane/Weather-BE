import apiClient from '../client';

export const weatherAPI = {
  /**
   * @param {string} location
   * @returns {Promise}
   */
  getCurrent: async (location) => {
    const { data } = await apiClient.post('/api/weather/current', { 
      location 
    });
    return data;
  },

  /**
   * @param {string} location
   * @param {number} days
   * @returns {Promise}
   */
  getForecast: async (location, days = 7) => {
    const { data } = await apiClient.post('/api/weather/forecast', { 
      location, 
      days 
    });
    return data;
  },
};