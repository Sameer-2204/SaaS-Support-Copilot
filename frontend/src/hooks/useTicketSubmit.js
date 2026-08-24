import { useState, useCallback } from 'react';
import { submitTicket } from '../lib/api';

/**
 * Custom hook for ticket submission with loading, error, and session state.
 */
export function useTicketSubmit() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [sessionId, setSessionId] = useState(null);

  const submit = useCallback(async (ticketText) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await submitTicket(ticketText, sessionId);
      setResult(data);
      setSessionId(data.session_id); // Persist for follow-ups
    } catch (err) {
      const message =
        err.response?.data?.detail ||
        err.message ||
        'An error occurred. Please try again.';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  const resetSession = useCallback(() => {
    setSessionId(null);
    setResult(null);
    setError(null);
  }, []);

  return { submit, isLoading, result, error, sessionId, reset, resetSession };
}
