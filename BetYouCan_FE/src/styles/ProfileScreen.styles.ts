import { StyleSheet } from "react-native";

export const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
  },
  heading: {
    fontSize: 22,
    fontWeight: "600",
    marginBottom: 12,
  },
  errorText: {
    color: "red",
    marginBottom: 10,
  },
  card: {
    borderWidth: 1,
    borderColor: "#e0e0e0",
    borderRadius: 10,
    padding: 14,
    gap: 8,
  },
  labelText: {
    fontWeight: "600",
  },
  refreshButton: {
    backgroundColor: "#111",
    paddingVertical: 12,
    borderRadius: 8,
    marginTop: 16,
    alignItems: "center",
  },
  refreshButtonText: {
    color: "#fff",
    fontWeight: "600",
  },
  logoutButton: {
    backgroundColor: "#c0392b",
    paddingVertical: 12,
    borderRadius: 8,
    marginTop: 12,
    alignItems: "center",
  },
  logoutButtonText: {
    color: "#fff",
    fontWeight: "600",
  },
});
