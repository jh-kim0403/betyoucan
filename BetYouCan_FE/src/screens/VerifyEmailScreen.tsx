import React, { useEffect, useState } from 'react';
import { ActivityIndicator, Text, TouchableOpacity, View, StyleSheet } from 'react-native';
import { useRoute, useNavigation } from '@react-navigation/native';
import { API_BASE_URL } from '../config/api';

export default function VerifyEmailScreen() {
  const route = useRoute();
  const navigation = useNavigation();
  const token = (route.params as any)?.token ?? null;
  console.log('VerifyEmailScreen token:', token);

  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!token) {
      setStatus('error');
      setErrorMessage('Verification link is missing a token.');
      return;
    }

    const verify = async () => {
      try {
        const response = await fetch(
          `${API_BASE_URL}/auth/manual/verify-email?token=${encodeURIComponent(token)}`
        );
        if (!response.ok) {
          const err = await response.json().catch(() => null);
          throw new Error(err?.detail || 'Verification failed.');
        }
        setStatus('success');
      } catch (error: any) {
        setStatus('error');
        setErrorMessage(error?.message ?? 'Verification failed.');
      }
    };

    void verify();
  }, [token]);

  return (
    <View style={styles.container}>
      {status === 'loading' && (
        <>
          <ActivityIndicator size="large" />
          <Text style={styles.message}>Verifying your email…</Text>
        </>
      )}

      {status === 'success' && (
        <>
          <Text style={styles.heading}>Email Verified!</Text>
          <Text style={styles.message}>Your email has been verified. You can now log in.</Text>
          <TouchableOpacity
            style={styles.button}
            // @ts-expect-error: app-wide nav types not yet defined
            onPress={() => navigation.navigate('Login')}
          >
            <Text style={styles.buttonText}>Go to Login</Text>
          </TouchableOpacity>
        </>
      )}

      {status === 'error' && (
        <>
          <Text style={styles.heading}>Verification Failed</Text>
          <Text style={styles.errorText}>{errorMessage}</Text>
          <TouchableOpacity
            style={styles.button}
            // @ts-expect-error: app-wide nav types not yet defined
            onPress={() => navigation.navigate('Login')}
          >
            <Text style={styles.buttonText}>Back to Login</Text>
          </TouchableOpacity>
        </>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
    gap: 16,
  },
  heading: {
    fontSize: 22,
    fontWeight: '600',
  },
  message: {
    fontSize: 15,
    textAlign: 'center',
    color: '#333',
  },
  errorText: {
    fontSize: 15,
    textAlign: 'center',
    color: '#c0392b',
  },
  button: {
    backgroundColor: '#111',
    paddingVertical: 12,
    paddingHorizontal: 32,
    borderRadius: 8,
    marginTop: 8,
  },
  buttonText: {
    color: '#fff',
    fontWeight: '600',
  },
});
