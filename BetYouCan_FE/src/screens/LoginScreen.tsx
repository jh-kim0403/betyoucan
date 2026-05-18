import React, { useContext, useState, useRef, useCallback } from 'react';
import { View, Text, TextInput, Animated, Pressable } from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';
import {
  GoogleSignin,
  statusCodes,
} from '@react-native-google-signin/google-signin';
import { useNavigation, useRoute, useFocusEffect } from '@react-navigation/native';

import AuthContext from '../context/AuthContext';
import { API_BASE_URL } from '../config/api';
import { styles, iconProps } from '../styles/LoginScreen.styles';

type LoginResponse = {
  user_id: string;
  email: string;
  first_name: string;
  last_name: string;
  access_token: string;
  refresh_token: string;
};

const LoginScreen = () => {
  const auth = useContext(AuthContext);
  const navigation = useNavigation();
  const route = useRoute();

  const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isInProgress, setIsInProgress] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const successMessage = (route.params as any)?.successMessage ?? null;

  const isSuccessResponse = (response: any): response is { data: any } => {
    return response && response.data;
  };

  const isErrorWithCode = (error: any): error is { code: string } => {
    return error && typeof error.code === 'string';
  };

  const handleAuthResponse = async (data: LoginResponse) => {
    if (!auth) {
      throw new Error('AuthContext not available');
    }
    await auth.login(data);
  };

  const clearError = useCallback(() => {
    setErrorMessage(null);
  }, []);

  useFocusEffect(
    useCallback(() => {
      setErrorMessage(null);
    }, [])
  );

  const loginScale = useRef(new Animated.Value(1)).current;
  const signUpScale = useRef(new Animated.Value(1)).current;

  const animateIn = (value: Animated.Value) => {
    Animated.spring(value, {
      toValue: 0.97,
      useNativeDriver: true,
      speed: 30,
      bounciness: 0,
    }).start();
  };

  const animateOut = (value: Animated.Value) => {
    Animated.spring(value, {
      toValue: 1,
      useNativeDriver: true,
      speed: 24,
      bounciness: 6,
    }).start();
  };

  const handleLogin = async () => {
    if (!email.trim() || !password.trim()) {
      setErrorMessage('Invalid Email/PW');
      return;
    }

    setIsInProgress(true);
    setErrorMessage(null);

    try {
      console.log('timezone:', Intl.DateTimeFormat().resolvedOptions().timeZone);
      const response = await fetch(`${API_BASE_URL}/auth/manual/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, timezone }),
      });

      if (!response.ok) {
        throw new Error('Invalid Email/PW');
      }

      const data: LoginResponse = await response.json();
      await handleAuthResponse(data);
    } catch (error: any) {
      setErrorMessage('Invalid Email/PW');
    } finally {
      setIsInProgress(false);
    }
  };

  const handleGoogleSignIn = async () => {
    setIsInProgress(true);
    setErrorMessage(null);

    try {
      await GoogleSignin.hasPlayServices();
      const response = await GoogleSignin.signIn();

      if (!isSuccessResponse(response)) {
        throw new Error('Google sign-in failed');
      }

      const idToken = response.data?.idToken;
      if (!idToken) {
        throw new Error('Missing Google ID token');
      }

      const apiResponse = await fetch(`${API_BASE_URL}/auth/google/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id_token: idToken }),
      });

      if (!apiResponse.ok) {
        const err = await apiResponse.json().catch(() => null);
        throw new Error(err?.detail || 'Google login failed');
      }

      const data: LoginResponse = await apiResponse.json();
      await handleAuthResponse(data);
    } catch (error: any) {
      if (isErrorWithCode(error)) {
        switch (error.code) {
          case statusCodes.IN_PROGRESS:
            setErrorMessage('Google sign-in is already in progress.');
            break;
          case statusCodes.PLAY_SERVICES_NOT_AVAILABLE:
            setErrorMessage('Google Play Services is not available.');
            break;
          default:
            setErrorMessage('Google sign-in failed');
            console.error('Google sign-in error:', error);
        }
      } else {
        setErrorMessage(error?.message ?? 'Google sign-in failed');
        console.error('Unknown Google sign-in error:', error);
      }
    } finally {
      setIsInProgress(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.contentWrapper}>
        <Text style={styles.title}>Welcome Back</Text>

        <View style={styles.inputContainer}>
          <View style={styles.inputInnerContainer}>
            <MaterialIcons {...iconProps.email} />
            <TextInput
              inputMode="email"
              placeholder="Email Address"
              value={email}
              onChangeText={(text) => { setEmail(text); clearError(); }}
              autoCapitalize="none"
              keyboardType="email-address"
              placeholderTextColor="#9aa3ad"
              style={{ flex: 1, marginLeft: 8, color: '#f3f4f6', fontSize: 16 }}
            />
          </View>
        </View>

        <View style={styles.inputContainer}>
          <View style={styles.inputInnerContainer}>
            <MaterialIcons {...iconProps.password} />
            <TextInput
              placeholder="Password"
              secureTextEntry
              value={password}
              onChangeText={(text) => { setPassword(text); clearError(); }}
              autoCapitalize="none"
              placeholderTextColor="#9aa3ad"
              style={{ flex: 1, marginLeft: 8, color: '#f3f4f6', fontSize: 16 }}
            />
          </View>
        </View>

        {successMessage ? (
          <Text style={styles.successText}>{successMessage}</Text>
        ) : null}

        {errorMessage ? (
          <Text style={styles.errorText}>{errorMessage}</Text>
        ) : null}

        <Animated.View
          style={[
            styles.primaryButtonContainer,
            { transform: [{ scale: loginScale }] },
          ]}
        >
          <Pressable
            onPressIn={() => animateIn(loginScale)}
            onPressOut={() => animateOut(loginScale)}
            onPress={handleLogin}
            disabled={isInProgress}
            style={styles.primaryButton}
          >
            <Text style={styles.primaryButtonText}>Login</Text>
          </Pressable>
        </Animated.View>

        <Animated.View
          style={[
            styles.signUpButtonContainer,
            { transform: [{ scale: signUpScale }] },
          ]}
        >
          <Pressable
            onPressIn={() => animateIn(signUpScale)}
            onPressOut={() => animateOut(signUpScale)}
            onPress={() => {
              // @ts-expect-error app-wide navigation types not defined yet
              navigation.navigate('SignUp');
            }}
            disabled={isInProgress}
            style={styles.secondaryButton}
          >
            <Text style={styles.secondaryButtonText}>Sign Up</Text>
          </Pressable>
        </Animated.View>
      </View>
    </View>
  );
};

export default LoginScreen;