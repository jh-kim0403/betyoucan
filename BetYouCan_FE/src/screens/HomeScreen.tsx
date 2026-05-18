import React, { useCallback, useContext, useEffect, useMemo, useState } from "react";
import {
  ActivityIndicator,
  FlatList,
  Pressable,
  Text,
  View,
} from "react-native";
import AuthContext from "../context/AuthContext";
import {useNavigation } from "@react-navigation/native";
import { API_BASE_URL } from "../config/api";
import { styles } from "../styles/HomeScreen.styles";

type Goal = {
  id?: string | number;
  title?: string;
  name?: string;
  description?: string;
  deadline?: string;
  created_at?: string;
  updated_at?: string;
  status?: string;
  quiz_question_status?: string;
  verification_status?: string;
  goal_type_id?: string;
  goal_type_name?: string;
  verification_type?: string;
  verification_updated_at?: string;
};

type UserProfile = {
  first_name?: string;
  last_name?: string;
  email?: string;
  bounty_balance?: number;
};

const getGoalDateValue = (goal: Goal): number => {
  const raw = goal.deadline || goal.created_at || goal.updated_at;
  if (!raw) return 0;
  const parsed = Date.parse(raw);
  return Number.isNaN(parsed) ? 0 : parsed;
};

const formatGoalDate = (goal: Goal): string | null => {
  const raw = goal.deadline || goal.created_at || goal.updated_at;
  if (!raw) return null;

  const parsed = Date.parse(raw);
  if (Number.isNaN(parsed)) return raw;

  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "2-digit",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(parsed));
};

const shouldShowVerifyButton = (goal: Goal): boolean => {
  const isQuizReady =
    goal.verification_type === "quiz" &&
    goal.quiz_question_status === "created" &&
    goal.verification_status === "not_started"

  const isExistingPhotoGoal =
    goal.verification_type === "photo" &&
    goal.verification_status !== "completed" &&
    goal.verification_status !== "failed";

  return isQuizReady || isExistingPhotoGoal;
};

const formatBountyAmount = (value: number): string => {
  return new Intl.NumberFormat(undefined, {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(value);
};

export default function HomeScreen() {
  const auth = useContext(AuthContext);
  const token = auth?.token ?? null;
  const authFetch = auth?.authFetch;
  const navigation = useNavigation();

  const [goals, setGoals] = useState<Goal[]>([]);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isProfileLoading, setIsProfileLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const fetchGoals = useCallback(async () => {
    if (!token) return;

    const response = await (authFetch ?? fetch)(`${API_BASE_URL}/goals/getcurrentgoals`, {
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error("Failed to load goals");
    }

    const data = await response.json();
    const normalized = Array.isArray(data) ? data : data?.data ?? [];
    setGoals(normalized);
  }, [token, authFetch]);

  const fetchProfile = useCallback(async () => {
    if (!token) return;

    const response = await (authFetch ?? fetch)(`${API_BASE_URL}/user/profile`, {
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error("Failed to load profile");
    }

    const data = await response.json();
    setProfile(data);
  }, [token, authFetch]);

  const reloadHome = useCallback(
    async (isRefresh = false) => {
      if (!token) return;

      if (isRefresh) {
        setIsRefreshing(true);
      } else {
        setIsLoading(true);
      }

      setIsProfileLoading(true);
      setErrorMessage(null);

      try {
        await Promise.all([fetchGoals(), fetchProfile()]);
      } catch (error: any) {
        setErrorMessage("Failed to reload home");
        console.error("Failed to reload home", error);
      } finally {
        setIsLoading(false);
        setIsRefreshing(false);
        setIsProfileLoading(false);
      }
    },
    [token, fetchGoals, fetchProfile]
  );

  React.useEffect(() => {
    void reloadHome(false);
  }, [reloadHome]);

  const sortedGoals = useMemo(() => {
    return [...goals].sort((a, b) => getGoalDateValue(a) - getGoalDateValue(b));
  }, [goals]);

  const firstName = profile?.first_name?.trim() || "Dream";
  const lastName = profile?.last_name?.trim() || "Studio";
  const bountyValue =  profile?.bounty_balance ?? 0;

  if (!token) {
    return (
      <View style={styles.missingTokenContainer}>
        <Text style={styles.missingTokenText}>Missing access token. Please log in again.</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.contentWrapper}>
        <View style={styles.profileCard}>
          <View style={styles.profileTopRow}>
            <View style={styles.nameBlock}>
              <Text style={styles.nameLine}>{firstName},</Text>
              <Text style={styles.nameLine}>{lastName}</Text>
            </View>

            <View style={styles.bountyBlock}>
              <Text style={styles.bountyLabel}>Bounty</Text>
              {isProfileLoading ? (
                <ActivityIndicator size="small" color="#aeb4bd" />
              ) : (
                <Text style={styles.bountyValue}>{formatBountyAmount(bountyValue)}</Text>
              )}
            </View>
          </View>

          <View style={styles.profileActionRow}>
            <Pressable
              style={styles.logoutLink}
              onPress={async () => {
                await auth?.logout?.();
              }}
            >
              {({ pressed }) => (
                <Text
                  style={[
                    styles.logoutLinkText,
                    pressed && styles.logoutLinkTextPressed,
                  ]}
                >
                  Log out
                </Text>
              )}
            </Pressable>

            <Pressable
              style={styles.fundsLink}
              onPress={() => {
                // @ts-expect-error: app-wide nav types not yet defined
                navigation.navigate("PurchaseBountyAndWithdrawl");
              }}
            >
              <Text style={styles.fundsLinkText}>Deposit & Withdraw</Text>
            </Pressable>
          </View>
        </View>

        <View style={styles.goalsSection}>
          <View style={styles.sectionHeader}>
            <Text style={styles.heading}>Current Goals</Text>
            <Text style={styles.goalCountText}>
              {sortedGoals.length} {sortedGoals.length === 1 ? "goal" : "goals"}
            </Text>
          </View>

          {isLoading ? (
            <ActivityIndicator size="large" color="#aeb4bd" style={styles.loadingIndicator} />
          ) : null}

          {errorMessage ? <Text style={styles.errorText}>{errorMessage}</Text> : null}

          <FlatList
            data={sortedGoals}
            keyExtractor={(item, index) => String(item.id ?? index)}
            contentContainerStyle={styles.listContent}
            showsVerticalScrollIndicator={false}
            alwaysBounceVertical={true}
            refreshing={isRefreshing}
            onRefresh={() => {
              void reloadHome(true);
            }}
            renderItem={({ item }) => (
              <View style={styles.goalItem}>
                <View style={styles.goalHeader}>
                  <View style={{ flex: 1, marginRight: 10 }}>
                    <Text style={styles.goalTitle}>{item.title || item.name || "Untitled Goal"}</Text>
                    {item.goal_type_name ? (
                      <Text style={styles.goalTypeName}>{item.goal_type_name}</Text>
                    ) : null}
                  </View>

                  {item.verification_type === "quiz" &&
                  (item.quiz_question_status === "pending") ? (
                    <Text style={styles.pendingQuizText}>Quiz being created</Text>
                  ) : shouldShowVerifyButton(item) ? (
                    <Pressable
                      style={styles.verifyButton}
                      onPress={() => {
                        // @ts-expect-error: app-wide nav types not yet defined
                        navigation.navigate("Verification", {
                          goalId: item.id,
                          goalTypeId: item.goal_type_id,
                          goalVerificationType: item.verification_type,
                        });
                      }}
                    >
                      <Text style={styles.verifyButtonText}>Verify</Text>
                    </Pressable>
                  ) : null}
                </View>

                {item.verification_status === "completed" ? (
                  <Text style={styles.approvedText}>Completed</Text>
                ) : item.verification_status === "failed" ? (
                  <Text style={styles.rejectedText}>Failed</Text>
                ) : null}

                {item.description ? (
                  <Text style={styles.descriptionText} numberOfLines={3}>
                    {item.description}
                  </Text>
                ) : null}

                {item.deadline || item.created_at || item.updated_at ? (
                  <Text style={styles.dateText}>{formatGoalDate(item)}</Text>
                ) : null}
              </View>
            )}
            ListEmptyComponent={
              !isLoading ? <Text style={styles.emptyText}>No goals yet.</Text> : null
            }
          />
        </View>

        <View style={styles.bottomActionSection}>
          <View style={styles.actionRow}>
            <Pressable
              style={[styles.actionButton, styles.primaryActionButton]}
              onPress={() => {
                // @ts-expect-error: app-wide nav types not yet defined
                navigation.navigate("AddNewGoal");
              }}
            >
              <Text style={styles.primaryActionText}>Add New Goal</Text>
            </Pressable>

            <Pressable
              style={[styles.actionButton, styles.secondaryActionButton]}
              onPress={() => {
                // @ts-expect-error: app-wide nav types not yet defined
                navigation.navigate("PastGoals");
              }}
            >
              <Text style={styles.secondaryActionText}>Past Goals</Text>
            </Pressable>
          </View>
        </View>
      </View>
    </View>
  );
}