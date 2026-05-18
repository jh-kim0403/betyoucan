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
  danger: "#ff8c96",
};

export const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },

  scrollContent: {
    flexGrow: 1,
    paddingHorizontal: 20,
    paddingTop: isTablet ? height * 0.06 : 20,
    paddingBottom: 28,
  },

  contentWrapper: {
    width: "100%",
    maxWidth: contentWidth,
    alignSelf: "center",
  },

  heading: {
    fontSize: isTablet ? 30 : 26,
    fontWeight: "700",
    color: COLORS.textPrimary,
    marginBottom: 8,
    letterSpacing: 0.2,
  },

  subtitle: {
    color: COLORS.textSecondary,
    fontSize: isTablet ? 16 : 14,
    marginBottom: 18,
  },

  formCard: {
    backgroundColor: COLORS.surface,
    borderWidth: 0.3,
    borderColor: COLORS.borderSoft,
    borderRadius: isTablet ? 22 : 20,
    paddingHorizontal: 16,
    paddingVertical: 16,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.14,
    shadowRadius: 8,
    elevation: 2,
  },

  formSection: {
    paddingVertical: 4,
  },

  sectionDivider: {
    height: 1,
    backgroundColor: "rgba(255,255,255,0.08)",
    marginVertical: 10,
  },

  sectionTitle: {
    fontSize: isTablet ? 18 : 16,
    fontWeight: "600",
    color: COLORS.textPrimary,
    marginBottom: 12,
  },

  inputLabel: {
    marginBottom: 8,
    color: COLORS.textSecondary,
    fontSize: 14,
    fontWeight: "500",
  },

  inlineSelector: {
    borderRadius: isTablet ? 20 : 18,
    overflow: "hidden",
  },

  selectorToggle: {
    minHeight: isTablet ? 58 : 54,
    paddingHorizontal: 16,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    backgroundColor: COLORS.surfaceSecondary,
    borderWidth: 0.3,
    borderColor: COLORS.borderSoft,
    borderRadius: isTablet ? 20 : 18,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 5 },
    shadowOpacity: 0.12,
    shadowRadius: 7,
    elevation: 2,
  },

  selectorLabel: {
    color: COLORS.textPrimary,
    fontSize: isTablet ? 16 : 15,
    fontWeight: "600",
    flex: 1,
    paddingRight: 12,
  },

  selectorToggleText: {
    color: COLORS.textSecondary,
    fontSize: isTablet ? 14 : 13,
    fontWeight: "500",
  },

  selectorList: {
    marginTop: 8,
    borderWidth: 0.3,
    borderColor: COLORS.borderSoft,
    borderRadius: isTablet ? 18 : 16,
    backgroundColor: COLORS.surfaceSecondary,
    overflow: "hidden",
  },

  loadingRow: {
    padding: 14,
  },

  errorText: {
    color: COLORS.danger,
  },

  selectorError: {
    paddingHorizontal: 14,
    paddingBottom: 14,
  },

  selectorItem: {
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderTopWidth: 0.3,
    borderTopColor: "rgba(255,255,255,0.12)",
  },

  selectorItemTitle: {
    color: COLORS.textPrimary,
    fontSize: isTablet ? 16 : 15,
    fontWeight: "500",
  },

  selectorItemDescription: {
    color: COLORS.textSecondary,
    marginTop: 4,
    fontSize: 13,
    lineHeight: 18,
  },

  chapterRow: {
    flexDirection: "row",
    gap: 12,
    marginTop: 12,
  },

  chapterField: {
    flex: 1,
  },

  input: {
    minHeight: isTablet ? 58 : 54,
    borderWidth: 0.3,
    borderColor: COLORS.borderSoft,
    borderRadius: isTablet ? 20 : 18,
    paddingHorizontal: 16,
    paddingVertical: 14,
    backgroundColor: COLORS.surfaceSecondary,
    color: COLORS.textPrimary,
    fontSize: isTablet ? 16 : 15,
    justifyContent: "center",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 5 },
    shadowOpacity: 0.12,
    shadowRadius: 7,
    elevation: 2,
  },

  inputText: {
    color: COLORS.textPrimary,
    fontSize: isTablet ? 16 : 15,
  },

  placeholderText: {
    color: "#9aa3ad",
    fontSize: isTablet ? 16 : 15,
  },

  multilineInput: {
    minHeight: 110,
    textAlignVertical: "top",
  },

  helperText: {
    color: COLORS.textMuted,
    marginTop: 8,
    fontSize: 13,
    lineHeight: 18,
  },

  inlineErrorText: {
    color: COLORS.danger,
    marginTop: 8,
    fontSize: 13,
  },

  submitError: {
    color: COLORS.danger,
    marginTop: 14,
    marginBottom: 6,
    fontSize: 14,
    textAlign: "center",
  },

  submitButton: {
    minHeight: isTablet ? 60 : 54,
    borderRadius: isTablet ? 20 : 18,
    alignItems: "center",
    justifyContent: "center",
    marginTop: 16,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 7 },
    shadowOpacity: 0.16,
    shadowRadius: 9,
    elevation: 3,
  },

  submitButtonActive: {
    backgroundColor: COLORS.surfacePrimary,
    borderWidth: 0.3,
    borderColor: COLORS.borderSoft,
  },

  submitButtonDisabled: {
    backgroundColor: COLORS.surfacePrimary,
    opacity: 0.6,
    borderWidth: 0.3,
    borderColor: COLORS.borderSoft,
  },

  submitButtonText: {
    color: COLORS.textPrimary,
    fontWeight: "600",
    fontSize: isTablet ? 17 : 15,
  },
});