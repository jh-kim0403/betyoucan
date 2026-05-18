import React, { useContext, useEffect, useState } from "react";
import { ActivityIndicator, Text, TouchableOpacity, View } from "react-native";
import AuthContext from "../context/AuthContext";
import { API_BASE_URL } from "../config/api";
import { styles } from "../styles/ProfileScreen.styles";

type UserProfile = {
  first_name: string;
  last_name: string;
  email: string;
  bounty_amount?: number;
  bounty_balance?: number;
};

export default function ProfileScreen() {
  const auth = useContext(AuthContext);
  const authFetch = auth?.authFetch;
  const token = auth?.token ?? null;
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const fetchProfile = async () => {
    if (!token) {
      setErrorMessage("Missing access token. Please log in again.");
      return;
    }
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const response = await (authFetch ?? fetch)(`${API_BASE_URL}/user/profile`, {
        headers: {
          "Content-Type": "application/json",
        },
      });
      if (!response.ok) {
        const err = await response.json().catch(() => null);
        throw new Error(err?.detail || "Failed to load profile");
      }
      const data = await response.json();
      setProfile(data);
    } catch (error: any) {
      setErrorMessage(error?.message ?? "Failed to load profile");
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      await auth?.logout();
    } finally {
      setIsLoggingOut(false);
    }
  };

  useEffect(() => {
    void fetchProfile();
  }, [token]);

  const bountyValue = profile?.bounty_amount ?? profile?.bounty_balance ?? 0;

  return (
    <View style={styles.container}>
      <Text style={styles.heading}>Profile</Text>

      {isLoading ? <ActivityIndicator size="large" /> : null}
      {errorMessage ? <Text style={styles.errorText}>{errorMessage}</Text> : null}

      {profile ? (
        <View style={styles.card}>
          <Text>
            <Text style={styles.labelText}>First name: </Text>
            {profile.first_name || "-"}
          </Text>
          <Text>
            <Text style={styles.labelText}>Last name: </Text>
            {profile.last_name || "-"}
          </Text>
          <Text>
            <Text style={styles.labelText}>Email: </Text>
            {profile.email || "-"}
          </Text>
          <Text>
            <Text style={styles.labelText}>Bounty amount: </Text>{bountyValue}
          </Text>
        </View>
      ) : null}

      <TouchableOpacity
        style={styles.refreshButton}
        onPress={() => { void fetchProfile(); }}
        disabled={isLoading}
      >
        <Text style={styles.refreshButtonText}>Refresh Profile</Text>
      </TouchableOpacity>

      <TouchableOpacity
        style={styles.logoutButton}
        onPress={() => { void handleLogout(); }}
        disabled={isLoggingOut}
      >
        <Text style={styles.logoutButtonText}>
          {isLoggingOut ? "Logging out…" : "Log Out"}
        </Text>
      </TouchableOpacity>
    </View>
  );
}
