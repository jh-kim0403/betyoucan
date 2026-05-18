import React from "react";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import HomeScreen from "./HomeScreen";
import VerificationScreen from "./VerificationScreen";
import AddNewGoalScreen from "./AddNewGoalScreen";
import PurchaseBountyAndWithdrawlScreen from "./PurchaseBountyAndWithdrawlScreen";
import PastGoalsScreen from "./PastGoalsScreen";
import ProfileScreen from "./ProfileScreen";

const Stack = createNativeStackNavigator();

export default function AuthenticatedScreens() {
  return (
    <Stack.Navigator>
      <Stack.Screen
        name="Home"
        component={HomeScreen}
        options={{ title: "Home" }}
      />
      <Stack.Screen
        name="Verification"
        component={VerificationScreen}
        options={{ title: "Verification" }}
      />
      <Stack.Screen
        name="AddNewGoal"
        component={AddNewGoalScreen}
        options={{ title: "Add New Goal" }}
      />
      <Stack.Screen
        name="PurchaseBountyAndWithdrawl"
        component={PurchaseBountyAndWithdrawlScreen}
        options={{ title: "Purchase Bounty" }}
      />
      <Stack.Screen
        name="PastGoals"
        component={PastGoalsScreen}
        options={{ title: "Past Goals" }}
      />
      <Stack.Screen
        name="Profile"
        component={ProfileScreen}
        options={{ title: "Profile" }}
      />
    </Stack.Navigator>
  );
}
