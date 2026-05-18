import { ActivityIndicator, StatusBar, StyleSheet, View } from 'react-native';
import {
  SafeAreaProvider,
} from 'react-native-safe-area-context';
import LoginScreen from './src/screens/LoginScreen';
import SignUpScreen from './src/screens/SignUpScreen';
import VerifyEmailScreen from './src/screens/VerifyEmailScreen';
import AuthenticatedScreens from './src/screens/AuthenticatedScreens';
import AuthContextProvider from './src/auth/AuthProvider';
import { DefaultTheme, NavigationContainer, createNavigationContainerRef } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import React, { useContext } from 'react';

const navigationRef = createNavigationContainerRef<any>();
import AuthContext from './src/context/AuthContext';
import { StripeProvider } from '@stripe/stripe-react-native';

const STRIPE_PUBLISHABLE_KEY = 'pk_test_51IaRKKFi3VeKp8O4EAEuWDIo4VYcQqgdJeE9TEnQbxNJTwl4OBstWX8zjUhnvhUbFYg2T5hLeGtWatpnW3kLKM5s00XdN4EUYu'; //change later

const linking = {
  prefixes: ['betyoucan://'],
  config: {
    screens: {
      Login: 'login',
      SignUp: 'signup',
      VerifyEmail: 'verify-email',
    },
  },
};

const navTheme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    background: '#1f1f1f',
    card: '#1f1f1f',
    text: '#f3f4f6',
    border: 'rgba(255,255,255,0.10)',
    primary: '#5d6976',
  },
};

const Stack = createNativeStackNavigator();

function Navigation() {
  const auth = useContext(AuthContext);
  const user = auth?.isLoggedIn ?? false;
  const isAuthBootstrapping = auth?.isAuthBootstrapping ?? true;

  if (isAuthBootstrapping) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#aeb4bd" />
      </View>
    );
  }

  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: {
          backgroundColor: '#1f1f1f',
        },
        headerTintColor: '#f3f4f6',
        headerTitleStyle: {
          color: '#f3f4f6',
          fontWeight: '600',
        },
        headerShadowVisible: false,
        contentStyle: {
          backgroundColor: '#1f1f1f',
        },
      }}
    >
      {!user ? (
        <>
          <Stack.Screen
            name="Login"
            component={LoginScreen}
            options={{ title: '', headerBackVisible: false }}
          />
          <Stack.Screen
            name="SignUp"
            component={SignUpScreen}
            options={{ title: '' }}
          />
          <Stack.Screen
            name="VerifyEmail"
            component={VerifyEmailScreen}
            options={{ title: 'Verify Email', headerBackVisible: false }}
          />
        </>
      ) : (
        <Stack.Screen
          name="App"
          component={AuthenticatedScreens}
          options={{ headerShown: false }}
        />
      )}
    </Stack.Navigator>
  );
}

export default function App() {
  return (
    <SafeAreaProvider>
      <StatusBar
        barStyle="light-content"
        backgroundColor="#1f1f1f"
      />
      <AuthContextProvider>
        <StripeProvider publishableKey={STRIPE_PUBLISHABLE_KEY}>
          <NavigationContainer ref={navigationRef} linking={linking} theme={navTheme} fallback={<ActivityIndicator size="large" color="#aeb4bd" />}>
            <Navigation />
          </NavigationContainer>
        </StripeProvider>
      </AuthContextProvider>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#1f1f1f',
  },
});