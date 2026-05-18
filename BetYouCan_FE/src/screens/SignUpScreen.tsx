import React, { useContext, useState, useCallback } from 'react';
import { View, Text, TextInput, Pressable, KeyboardAvoidingView, Platform } from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';
import { GoogleSigninButton, statusCodes, GoogleSignin } from '@react-native-google-signin/google-signin';
import AuthContext from '../context/AuthContext';
import { API_BASE_URL } from '../config/api';
import { CommonActions, useNavigation, useFocusEffect } from '@react-navigation/native';
import styles, { iconProps } from '../styles/SignUpScreen.styles';

type LoginResponse = {
  user_id: string;
  email: string;
  first_name: string;
  last_name: string;
  access_token: string;
  refresh_token: string;
};

export default function SignUpScreen() {
  const auth = useContext(AuthContext);
  const navigation = useNavigation();

  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isInProgress, setIsInProgress] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

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

const handleManualSignup = async () => {
    setIsInProgress(true);
    setErrorMessage(null);

    try {
        const response = await fetch(`${API_BASE_URL}/auth/manual/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            email,
            password,
            first_name: firstName,
            last_name: lastName,
        }),
        });

        if (!response.ok) {
        throw new Error('Invalid input');
        }

        navigation.dispatch(
          CommonActions.reset({
            index: 0,
            routes: [
              {
                name: 'Login',
                params: {
                  successMessage: 'Sign up successful. Please verify your email.',
                },
              },
            ],
          })
        );
    } catch (error: any) {
        setErrorMessage('Invalid input');
    } finally {
        setIsInProgress(false);
    }
    };

  const googleSignUp = async () => {
    setIsInProgress(true);
    setErrorMessage(null);

    try {
      await GoogleSignin.hasPlayServices();
      const response = await GoogleSignin.signIn();

      if (!isSuccessResponse(response)) return;

      const idToken = response.data?.idToken;
      if (!idToken) {
        throw new Error('Missing Google id token');
      }

      const apiResponse = await fetch(`${API_BASE_URL}/auth/google/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id_token: idToken }),
      });

      if (!apiResponse.ok) {
        const err = await apiResponse.json().catch(() => null);
        throw new Error(err?.detail || 'Google sign up failed');
      }

      const data: LoginResponse = await apiResponse.json();

      if (data.access_token && data.refresh_token) {
        await handleAuthResponse(data);
      } else {
        throw new Error('Missing tokens from Google sign up response');
      }
    } catch (error) {
      if (isErrorWithCode(error)) {
        switch (error.code) {
          case statusCodes.IN_PROGRESS:
            break;
          case statusCodes.PLAY_SERVICES_NOT_AVAILABLE:
            break;
          default:
            console.error('An error occurred during Google sign up', error);
        }
      } else {
        console.error('An unknown error occurred during Google sign up', error);
      }

      setErrorMessage('Google sign-up failed');
    } finally {
      setIsInProgress(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <View style={styles.screenInner}>
        <View style={styles.contentWrapper}>
          <Text style={styles.title}>Create Account</Text>
          <Text style={styles.subtitle}>Sign up to start using DreamStudio.</Text>

          <View style={styles.inputContainer}>
            <View style={styles.inputInnerContainer}>
              <MaterialIcons {...iconProps.person} />
              <TextInput
                placeholder="First Name"
                placeholderTextColor={styles.placeholderColor.color}
                value={firstName}
                onChangeText={(text) => { setFirstName(text); clearError(); }}
                autoCapitalize="words"
                style={[styles.inputText, { flex: 1 }]}
              />
            </View>
          </View>

          <View style={styles.inputContainer}>
            <View style={styles.inputInnerContainer}>
              <MaterialIcons {...iconProps.person} />
              <TextInput
                placeholder="Last Name"
                placeholderTextColor={styles.placeholderColor.color}
                value={lastName}
                onChangeText={(text) => { setLastName(text); clearError(); }}
                autoCapitalize="words"
                style={[styles.inputText, { flex: 1 }]}
              />
            </View>
          </View>

          <View style={styles.inputContainer}>
            <View style={styles.inputInnerContainer}>
              <MaterialIcons {...iconProps.email} />
              <TextInput
                inputMode="email"
                placeholder="Email Address"
                placeholderTextColor={styles.placeholderColor.color}
                value={email}
                onChangeText={(text) => { setEmail(text); clearError(); }}
                autoCapitalize="none"
                style={[styles.inputText, { flex: 1 }]}
              />
            </View>
          </View>

          <View style={styles.inputContainer}>
            <View style={styles.inputInnerContainer}>
              <MaterialIcons {...iconProps.password} />
              <TextInput
                placeholder="Password"
                placeholderTextColor={styles.placeholderColor.color}
                secureTextEntry
                value={password}
                onChangeText={(text) => { setPassword(text); clearError(); }}
                autoCapitalize="none"
                style={[styles.inputText, { flex: 1 }]}
              />
            </View>
          </View>

          {errorMessage ? <Text style={styles.errorText}>{errorMessage}</Text> : null}

          <View style={styles.primaryButtonContainer}>
            <Pressable
              onPress={handleManualSignup}
              disabled={isInProgress}
              style={[styles.primaryButton, isInProgress && styles.primaryButtonDisabled]}
            >
              <Text style={styles.primaryButtonText}>Sign Up</Text>
            </Pressable>
          </View>

          {/*
          <GoogleSigninButton
            size={GoogleSigninButton.Size.Wide}
            color={GoogleSigninButton.Color.Dark}
            onPress={googleSignUp}
            disabled={isInProgress}
          />
          */}
        </View>
      </View>
    </KeyboardAvoidingView>
  );
}