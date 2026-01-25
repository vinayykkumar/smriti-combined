import React, { createContext, useState, useCallback } from 'react';
import { fetchTodayQuote } from '../services/api/quotes';

// Create the Quote Context
export const QuoteContext = createContext();

/**
 * QuoteProvider - Provides quote state and methods to the entire app
 *
 * This context manages:
 * - Today's quote data (cached)
 * - Quote popup visibility
 * - Methods to open/close popup and refresh quote
 */
export function QuoteProvider({ children }) {
    // Popup visibility state
    const [isQuotePopupOpen, setIsQuotePopupOpen] = useState(false);

    // Today's quote data
    const [todayQuote, setTodayQuote] = useState(null);

    // Loading state
    const [isLoading, setIsLoading] = useState(false);

    // Error state
    const [error, setError] = useState(null);

    // Last fetch timestamp (to avoid refetching too frequently)
    const [lastFetchTime, setLastFetchTime] = useState(null);

    /**
     * Open the quote popup
     * Optionally fetches fresh data if needed
     */
    const openQuotePopup = useCallback(async (forceRefresh = false) => {
        setIsQuotePopupOpen(true);

        // Fetch data if we don't have it or if force refresh requested
        const shouldFetch = forceRefresh ||
            !todayQuote ||
            !lastFetchTime ||
            (Date.now() - lastFetchTime > 5 * 60 * 1000); // 5 minute cache

        if (shouldFetch) {
            await refreshTodayQuote();
        }
    }, [todayQuote, lastFetchTime]);

    /**
     * Close the quote popup
     */
    const closeQuotePopup = useCallback(() => {
        setIsQuotePopupOpen(false);
    }, []);

    /**
     * Fetch fresh quote data from API
     */
    const refreshTodayQuote = useCallback(async () => {
        setIsLoading(true);
        setError(null);

        try {
            const data = await fetchTodayQuote();
            setTodayQuote(data);
            setLastFetchTime(Date.now());
        } catch (err) {
            console.error('Failed to fetch today\'s quote:', err);
            setError(err.message || 'Failed to load quote');
            // Keep old data if we have it
        } finally {
            setIsLoading(false);
        }
    }, []);

    /**
     * Clear quote data (e.g., on logout)
     */
    const clearQuoteData = useCallback(() => {
        setTodayQuote(null);
        setLastFetchTime(null);
        setError(null);
        setIsQuotePopupOpen(false);
    }, []);

    const value = {
        // State
        isQuotePopupOpen,
        todayQuote,
        isLoading,
        error,

        // Methods
        openQuotePopup,
        closeQuotePopup,
        refreshTodayQuote,
        clearQuoteData,
    };

    return (
        <QuoteContext.Provider value={value}>
            {children}
        </QuoteContext.Provider>
    );
}
