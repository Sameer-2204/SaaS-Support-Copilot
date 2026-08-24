import axios from 'axios';

/**
 * Axios instance configured with the backend base URL and timeout.
 */
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000, // 30s — LLM generation can take time
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Submit a support ticket for processing.
 * @param {string} ticketText - The ticket content
 * @param {string|null} sessionId - Session ID for follow-up questions
 * @returns {Promise<object>} TicketResponse
 */
export async function submitTicket(ticketText, sessionId = null) {
  const { data } = await api.post('/api/tickets', {
    ticket_text: ticketText,
    session_id: sessionId,
  });
  return data;
}

/**
 * Get dashboard statistics.
 * @returns {Promise<object>} DashboardStats
 */
export async function getDashboardStats() {
  const { data } = await api.get('/api/dashboard/stats');
  return data;
}

/**
 * Get paginated ticket history.
 * @param {number} page
 * @param {number} limit
 * @returns {Promise<object>}
 */
export async function getTicketHistory(page = 1, limit = 20) {
  const { data } = await api.get('/api/dashboard/history', {
    params: { page, limit },
  });
  return data;
}

/**
 * Get UMAP projection data for the embedding visualizer.
 * @returns {Promise<object>} UmapResponse
 */
export async function getUmapData() {
  const { data } = await api.get('/api/visualize/umap');
  return data;
}

/**
 * Health check.
 * @returns {Promise<object>}
 */
export async function healthCheck() {
  const { data } = await api.get('/api/health');
  return data;
}

/**
 * Submit feedback/rating for a copilot response.
 * @param {string} ticketId - The ticket ID
 * @param {number} rating - Rating 1-5
 * @param {boolean} wasHelpful - Whether the response solved the issue
 * @param {string|null} comment - Optional written feedback
 * @returns {Promise<object>} FeedbackResponse
 */
export async function submitFeedback(ticketId, rating, wasHelpful, comment = null) {
  const { data } = await api.post('/api/feedback', {
    ticket_id: ticketId,
    rating,
    was_helpful: wasHelpful,
    comment,
  });
  return data;
}

/**
 * Get feedback analytics summary for the dashboard.
 * @returns {Promise<object>} FeedbackSummary
 */
export async function getFeedbackSummary() {
  const { data } = await api.get('/api/feedback/summary');
  return data;
}

/**
 * Get contact info for a specific product/department.
 * @param {string} product - Product name (shopify, stripe, twilio, vercel)
 * @returns {Promise<object>} ContactInfo
 */
export async function getContactInfo(product) {
  const { data } = await api.get(`/api/contacts/${product}`);
  return data;
}

/**
 * Get all department contacts.
 * @returns {Promise<object>}
 */
export async function getAllContacts() {
  const { data } = await api.get('/api/contacts');
  return data;
}

export default api;
