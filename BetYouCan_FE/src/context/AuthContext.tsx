import React, { createContext } from 'react';

export type LoginPayload = {
  user_id: string;
  email: string;
  first_name: string;
  last_name: string;
  access_token: string;
  refresh_token: string;
};

export interface AccessTokenContextType{
  userID: any;
  issue_at: any;
  exp: any;
}

export interface AuthContextType {
    user: any;
    token: string | null;
    isLoggedIn: boolean;
    isAuthBootstrapping: boolean;
  
    login: (data: LoginPayload) => Promise<void>;
    logout: () => Promise<void>;
    refreshToken: () => Promise<string | null>;
    authFetch: (input: RequestInfo, init?: RequestInit) => Promise<Response>;
    updateProfile: (changes: any) => Promise<void>;
  }

  const AuthContext = createContext<AuthContextType | undefined>(undefined);

export default AuthContext;
