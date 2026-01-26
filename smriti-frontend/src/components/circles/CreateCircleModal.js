/**
 * CreateCircleModal Component
 * Modal for creating a new circle or joining via invite code
 */
import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Modal,
  TextInput,
  TouchableOpacity,
  TouchableWithoutFeedback,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { COLORS, SPACING, TYPOGRAPHY, SHADOWS } from '../../styles/theme';

export default function CreateCircleModal({
  visible,
  onClose,
  onCreateCircle,
  onJoinCircle,
  loading = false
}) {
  const [mode, setMode] = useState('create'); // 'create' or 'join'
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [inviteCode, setInviteCode] = useState('');

  const resetForm = () => {
    setName('');
    setDescription('');
    setInviteCode('');
    setMode('create');
  };

  const handleClose = () => {
    resetForm();
    onClose?.();
  };

  const handleCreate = async () => {
    if (!name.trim()) {
      Alert.alert('Required', 'Please enter a circle name');
      return;
    }
    if (name.trim().length < 2) {
      Alert.alert('Invalid Name', 'Circle name must be at least 2 characters');
      return;
    }
    try {
      await onCreateCircle?.({
        name: name.trim(),
        description: description.trim() || undefined
      });
      handleClose();
    } catch (err) {
      Alert.alert('Error', err.message || 'Failed to create circle');
    }
  };

  const handleJoin = async () => {
    const code = inviteCode.trim().toUpperCase();
    if (!code) {
      Alert.alert('Required', 'Please enter an invite code');
      return;
    }
    if (code.length !== 8) {
      Alert.alert('Invalid Code', 'Invite code must be 8 characters');
      return;
    }
    try {
      await onJoinCircle?.(code);
      handleClose();
    } catch (err) {
      Alert.alert('Error', err.message || 'Failed to join circle');
    }
  };

  return (
    <Modal
      visible={visible}
      animationType="slide"
      transparent={true}
      onRequestClose={handleClose}
    >
      <TouchableWithoutFeedback onPress={handleClose}>
        <View style={styles.overlay}>
          <TouchableWithoutFeedback onPress={() => {}}>
            <KeyboardAvoidingView
              behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
              style={styles.keyboardView}
            >
              <View style={styles.container}>
                {/* Header */}
                <View style={styles.header}>
                  <Text style={styles.title}>
                    {mode === 'create' ? 'Create Circle' : 'Join Circle'}
                  </Text>
                  <TouchableOpacity onPress={handleClose} style={styles.closeButton}>
                    <Ionicons name="close" size={24} color={COLORS.text} />
                  </TouchableOpacity>
                </View>

                {/* Mode Toggle */}
                <View style={styles.toggleContainer}>
                  <TouchableOpacity
                    style={[styles.toggleButton, mode === 'create' && styles.toggleActive]}
                    onPress={() => setMode('create')}
                  >
                    <Ionicons
                      name="add-circle-outline"
                      size={18}
                      color={mode === 'create' ? COLORS.card : COLORS.textLight}
                    />
                    <Text style={[styles.toggleText, mode === 'create' && styles.toggleTextActive]}>
                      Create New
                    </Text>
                  </TouchableOpacity>
                  <TouchableOpacity
                    style={[styles.toggleButton, mode === 'join' && styles.toggleActive]}
                    onPress={() => setMode('join')}
                  >
                    <Ionicons
                      name="enter-outline"
                      size={18}
                      color={mode === 'join' ? COLORS.card : COLORS.textLight}
                    />
                    <Text style={[styles.toggleText, mode === 'join' && styles.toggleTextActive]}>
                      Join Existing
                    </Text>
                  </TouchableOpacity>
                </View>

                {/* Form */}
                {mode === 'create' ? (
                  <View style={styles.form}>
                    <Text style={styles.label}>Circle Name *</Text>
                    <TextInput
                      style={styles.input}
                      value={name}
                      onChangeText={setName}
                      placeholder="e.g., Family, Close Friends"
                      placeholderTextColor={COLORS.textLight}
                      maxLength={50}
                      autoFocus
                    />

                    <Text style={styles.label}>Description (optional)</Text>
                    <TextInput
                      style={[styles.input, styles.textArea]}
                      value={description}
                      onChangeText={setDescription}
                      placeholder="What's this circle about?"
                      placeholderTextColor={COLORS.textLight}
                      multiline
                      numberOfLines={3}
                      maxLength={200}
                    />

                    <Text style={styles.hint}>
                      Circles are small, intimate groups (max 5 members).
                      Once created, members can't leave - only unanimous deletion.
                    </Text>
                  </View>
                ) : (
                  <View style={styles.form}>
                    <Text style={styles.label}>Invite Code</Text>
                    <TextInput
                      style={[styles.input, styles.codeInput]}
                      value={inviteCode}
                      onChangeText={(text) => setInviteCode(text.toUpperCase())}
                      placeholder="XXXXXXXX"
                      placeholderTextColor={COLORS.textLight}
                      maxLength={8}
                      autoCapitalize="characters"
                      autoCorrect={false}
                      autoFocus
                    />

                    <Text style={styles.hint}>
                      Ask a circle member for their 8-character invite code.
                      Joining a circle is a lifetime commitment.
                    </Text>
                  </View>
                )}

                {/* Submit Button */}
                <TouchableOpacity
                  style={[styles.submitButton, loading && styles.submitButtonDisabled]}
                  onPress={mode === 'create' ? handleCreate : handleJoin}
                  disabled={loading}
                >
                  {loading ? (
                    <ActivityIndicator color={COLORS.card} />
                  ) : (
                    <>
                      <Ionicons
                        name={mode === 'create' ? 'add-circle' : 'enter'}
                        size={20}
                        color={COLORS.card}
                      />
                      <Text style={styles.submitText}>
                        {mode === 'create' ? 'Create Circle' : 'Join Circle'}
                      </Text>
                    </>
                  )}
                </TouchableOpacity>
              </View>
            </KeyboardAvoidingView>
          </TouchableWithoutFeedback>
        </View>
      </TouchableWithoutFeedback>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end',
  },
  keyboardView: {
    width: '100%',
  },
  container: {
    backgroundColor: COLORS.card,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: SPACING.lg,
    paddingBottom: SPACING.xl + 20,
    ...SHADOWS.medium,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: SPACING.md,
  },
  title: {
    ...TYPOGRAPHY.heading,
    color: COLORS.text,
  },
  closeButton: {
    padding: SPACING.xs,
  },
  toggleContainer: {
    flexDirection: 'row',
    backgroundColor: COLORS.background,
    borderRadius: 12,
    padding: 4,
    marginBottom: SPACING.lg,
  },
  toggleButton: {
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: SPACING.sm,
    borderRadius: 10,
  },
  toggleActive: {
    backgroundColor: COLORS.primary,
  },
  toggleText: {
    ...TYPOGRAPHY.caption,
    color: COLORS.textLight,
    marginLeft: 6,
    fontWeight: '500',
  },
  toggleTextActive: {
    color: COLORS.card,
  },
  form: {
    marginBottom: SPACING.lg,
  },
  label: {
    ...TYPOGRAPHY.caption,
    color: COLORS.text,
    fontWeight: '600',
    marginBottom: SPACING.xs,
  },
  input: {
    backgroundColor: COLORS.background,
    borderRadius: 12,
    padding: SPACING.md,
    ...TYPOGRAPHY.body,
    color: COLORS.text,
    marginBottom: SPACING.md,
  },
  textArea: {
    minHeight: 80,
    textAlignVertical: 'top',
  },
  codeInput: {
    fontSize: 24,
    letterSpacing: 4,
    textAlign: 'center',
    fontWeight: '600',
  },
  hint: {
    ...TYPOGRAPHY.caption,
    color: COLORS.textLight,
    fontStyle: 'italic',
    lineHeight: 18,
  },
  submitButton: {
    backgroundColor: COLORS.primary,
    borderRadius: 12,
    paddingVertical: SPACING.md,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },
  submitButtonDisabled: {
    opacity: 0.6,
  },
  submitText: {
    ...TYPOGRAPHY.body,
    color: COLORS.card,
    fontWeight: '600',
    marginLeft: SPACING.sm,
  },
});
