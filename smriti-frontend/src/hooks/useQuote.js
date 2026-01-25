import { useContext } from 'react';
import { QuoteContext } from '../contexts/QuoteContext';

/**
 * Hook to access Quote context
 * @returns {Object} Quote context value
 * @throws {Error} If used outside QuoteProvider
 */
export function useQuote() {
    const context = useContext(QuoteContext);

    if (!context) {
        throw new Error('useQuote must be used within a QuoteProvider');
    }

    return context;
}
