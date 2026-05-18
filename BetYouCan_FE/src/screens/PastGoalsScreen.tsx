import React from "react";
import { Text, View } from "react-native";
import { styles } from "../styles/PastGoalsScreen.styles";

export default function PastGoalsScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.heading}>Past Goals</Text>
      <Text style={styles.bodyText}>Review completed or expired goals here.</Text>
    </View>
  );
}
