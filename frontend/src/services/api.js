import axios from "axios";

const API_BASE = "http://127.0.0.1:8000/api/v1";

export const analyzeText = async (text) => {
  const response = await axios.post(`${API_BASE}/analysis`, { text });
  return response.data;
};

export const sendFeedback = async (rating) => {
  const response = await axios.post(`${API_BASE}/feedback`, { rating });
  return response.data;
};

export const verifySource = async (url) => {
  const response = await axios.post(`${API_BASE}/verification`, { url });
  return response.data;
};