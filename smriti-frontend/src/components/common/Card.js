import React from 'react';
import { View, StyleSheet } from 'react-native';
import { COLORS } from '../../styles/theme';

/**
 * Reusable Card Component
 * @param {ReactNode} children - Card content
 * @param {object} style - Additional styles
 */
export default function Card({ children, style }) {
    return (
        <View style={[styles.card, style]}>
            {children}
        </View>
    );
}

const styles = StyleSheet.create({
    card: {
        backgroundColor: '#FFFFFF',
        borderRadius: 16,
        padding: 16,
        marginBottom: 16,
        shadowColor: '#000',
        shadowOffset: {
            width: 0,
            height: 2,
        },
        shadowOpacity: 0.1,
        shadowRadius: 8,
        elevation: 3,
    },
});
