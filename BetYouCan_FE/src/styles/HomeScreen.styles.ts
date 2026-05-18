import { Dimensions, StyleSheet } from "react-native";

const { width, height } = Dimensions.get("window");
const isTablet = width >= 768;
const contentWidth = Math.min(width - 40, 560);

const COLORS = {
  background: "#1f1f1f",
  surface: "#2a2f36",
  surfaceSecondary: "#313842",
  surfacePrimary: "#5d6976",
  borderSoft: "rgba(255, 255, 255, 0.30)",
  textPrimary: "#f3f4f6",
  textSecondary: "#aeb4bd",
  textMuted: "#8f98a3",
  success: "#8fd6ae",
  danger: "#ff8c96",
};

export const styles = StyleSheet.create({
  missingTokenContainer: {
    flex: 1,
    backgroundColor: COLORS.background,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 24,
  },

  missingTokenText: {
    color: COLORS.textSecondary,
    fontSize: 16,
    textAlign: "center",
  },

  container: {
    flex: 1,
    backgroundColor: COLORS.background,
    paddingHorizontal: 20,
    paddingTop: isTablet ? height * 0.06 : 18,
    paddingBottom: 16,
  },

  contentWrapper: {
    width: "100%",
    maxWidth: contentWidth,
    alignSelf: "center",
    flex: 1,
  },

  profileCard: {
    backgroundColor: COLORS.surface,
    borderWidth: 0.3,
    borderColor: COLORS.borderSoft,
    borderRadius: isTablet ? 22 : 20,
    paddingHorizontal: isTablet ? 22 : 18,
    paddingTop: isTablet ? 20 : 18,
    paddingBottom: isTablet ? 16 : 14,
    marginBottom: 14,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 7 },
    shadowOpacity: 0.18,
    shadowRadius: 10,
    elevation: 3,
  },

  profileTopRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
    gap: 16,
  },

  nameBlock: {
    flex: 1,
    paddingRight: 8,
  },

  nameLine: {
    fontSize: isTablet ? 29 : 24,
    lineHeight: isTablet ? 34 : 29,
    fontWeight: "600",
    color: COLORS.textPrimary,
    letterSpacing: 0.2,
  },

  bountyBlock: {
    alignItems: "flex-end",
    justifyContent: "flex-start",
    minWidth: isTablet ? 140 : 112,
  },

  bountyLabel: {
    color: COLORS.textMuted,
    fontSize: isTablet ? 13 : 12,
    fontWeight: "600",
    marginBottom: 6,
    textTransform: "uppercase",
    letterSpacing: 0.8,
  },

  bountyValue: {
    color: COLORS.textPrimary,
    fontSize: isTablet ? 28 : 22,
    fontWeight: "700",
    textAlign: "right",
  },

  profileActionRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-end",
    marginTop: 16,
  },

  logoutLink: {
    paddingTop: 2,
    paddingBottom: 2,
    paddingRight: 10,
    marginTop: 6,
  },

  logoutLinkText: {
    color: "#8f98a3",
    fontSize: isTablet ? 13 : 12,
    fontWeight: "400",
  },

  logoutLinkTextPressed: {
    textDecorationLine: "underline",
  },

  fundsLink: {
    backgroundColor: COLORS.surfaceSecondary,
    borderWidth: 0.3,
    borderColor: COLORS.borderSoft,
    borderRadius: 999,
    paddingHorizontal: 12,
    paddingVertical: 8,
  },

  fundsLinkText: {
    color: COLORS.textSecondary,
    fontSize: isTablet ? 14 : 13,
    fontWeight: "600",
  },

  goalsSection: {
    flex: 1,
    minHeight: 0,
  },

  sectionHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-end",
    marginBottom: 14,
    gap: 12,
  },

  heading: {
    fontSize: isTablet ? 28 : 24,
    fontWeight: "700",
    color: COLORS.textPrimary,
    letterSpacing: 0.2,
  },

  goalCountText: {
    color: COLORS.textMuted,
    fontSize: isTablet ? 14 : 13,
    marginBottom: 3,
  },

  loadingIndicator: {
    marginTop: 4,
    marginBottom: 10,
  },

  errorText: {
    color: COLORS.danger,
    fontSize: 14,
    textAlign: "center",
    marginBottom: 12,
  },

  listContent: {
    paddingBottom: 12,
  },

  goalItem: {
    backgroundColor: COLORS.surface,
    borderWidth: 0.3,
    borderColor: COLORS.borderSoft,
    borderRadius: isTablet ? 20 : 18,
    paddingHorizontal: 16,
    paddingVertical: 15,
    marginBottom: 12,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.14,
    shadowRadius: 8,
    elevation: 2,
  },

  goalHeader: {
    flexDirection: "row",
    alignItems: "flex-start",
    justifyContent: "space-between",
    gap: 10,
  },

  goalTitle: {
    fontSize: isTablet ? 18 : 16,
    fontWeight: "600",
    color: COLORS.textPrimary,
  },

  goalTypeName: {
    fontSize: isTablet ? 13 : 12,
    color: COLORS.textMuted,
    marginTop: 2,
  },

  pendingQuizText: {
    color: COLORS.textSecondary,
    fontWeight: "600",
    fontSize: 13,
    marginTop: 2,
  },

  verifyButton: {
    minHeight: 36,
    borderRadius: 12,
    backgroundColor: COLORS.surfacePrimary,
    borderWidth: 0.3,
    borderColor: COLORS.borderSoft,
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: 14,
  },

  verifyButtonText: {
    color: COLORS.textPrimary,
    fontWeight: "600",
    fontSize: 13,
  },

  approvedText: {
    color: COLORS.success,
    fontWeight: "600",
    marginTop: 8,
    fontSize: 13,
  },

  rejectedText: {
    color: COLORS.danger,
    fontWeight: "600",
    marginTop: 8,
    fontSize: 13,
  },

  descriptionText: {
    color: COLORS.textSecondary,
    marginTop: 8,
    fontSize: 14,
    lineHeight: 20,
  },

  dateText: {
    color: COLORS.textMuted,
    marginTop: 8,
    fontSize: 13,
  },

  emptyText: {
    color: COLORS.textSecondary,
    textAlign: "center",
    marginTop: 28,
    fontSize: 15,
  },

  bottomActionSection: {
    paddingTop: 12,
    paddingBottom: 4,
    backgroundColor: COLORS.background,
  },

  actionRow: {
    flexDirection: "row",
    gap: 10,
  },

  actionButton: {
    flex: 1,
    minHeight: isTablet ? 58 : 52,
    borderRadius: isTablet ? 20 : 18,
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: 12,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 7 },
    shadowOpacity: 0.16,
    shadowRadius: 9,
    elevation: 3,
  },

  primaryActionButton: {
    backgroundColor: COLORS.surfacePrimary,
    borderWidth: 0.3,
    borderColor: COLORS.borderSoft,
  },

  secondaryActionButton: {
    backgroundColor: COLORS.surfaceSecondary,
    borderWidth: 0.3,
    borderColor: COLORS.borderSoft,
  },

  primaryActionText: {
    color: COLORS.textPrimary,
    fontWeight: "600",
    fontSize: isTablet ? 17 : 15,
    textAlign: "center",
  },

  secondaryActionText: {
    color: "#dde2e8",
    fontWeight: "600",
    fontSize: isTablet ? 17 : 15,
    textAlign: "center",
  },
});