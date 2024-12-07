import axios from 'axios';

const BASE_URL = 'http://127.0.0.1:5000';

const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  // Enable credentials
  withCredentials: true
});

class AnalysisServiceClass {
  async fetchAnalysis(endpoint) {
    try {
      const response = await apiClient.get(endpoint);
      return response.data;
    } catch (error) {
      console.error(`Error fetching data from ${endpoint}:`, error);
      
      if (error.response) {
        throw new Error(`Server responded with ${error.response.status}: ${error.response.data}`);
      } else if (error.request) {
        throw new Error('No response received from server. Check your network connection.');
      } else {
        throw new Error('Error setting up the request');
      }
    }
  }

  // Analysis methods
  async getStockAnalysis() {
    return this.fetchAnalysis('/analyze/stocks');
  }

  async getNewsAnalysis() {
    return this.fetchAnalysis('/analyze/news');
  }

  async getCryptoAnalysis() {
    return this.fetchAnalysis('/analyze/crypto');
  }

  async getTechTrends() {
    return this.fetchAnalysis('/analyze/trends/tech');
  }

  async getFinanceTrends() {
    return this.fetchAnalysis('/analyze/trends/finance');
  }

  async getEntertainmentTrends() {
    return this.fetchAnalysis('/analyze/trends/entertainment');
  }
}

export const AnalysisService = new AnalysisServiceClass();