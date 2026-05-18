import { Dimensions, StyleSheet } from "react-native";

const { width } = Dimensions.get("window");
const isTabletLike = width >= 768;

const COLORS = {
  background: "#1f1f1f",
  surfacePrimary: "#2a2f36",
  surfaceSecondary: "#313842",
  surfaceAccent: "#5d6976",
  borderStrong: "rgba(255,255,255,0.30)",
  borderSoft: "rgba(255,255,255,0.12)",
  textPrimary: "#f3f4f6",
  textSecondary: "#aeb4bd",
  textMuted: "#8f98a3",
  success: "#8fd6ae",
  danger: "#ff8c96",
  warning: "#d9c27a",
  overlay: "rgba(0,0,0,0.52)",
};

export const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  scrollContent: {
    flexGrow: 1,
  },
  container: {
    flex: 1,
    paddingHorizontal: isTabletLike ? 32 : 20,
    paddingTop: isTabletLike ? 40 : 28,
    paddingBottom: 28,
  },
  headerBlock: {
    marginBottom: 22,
  },
  heading: {
    fontSize: isTabletLike ? 30 : 26,
    fontWeight: "700",
    color: COLORS.textPrimary,
    marginBottom: 10,
    letterSpacing: 0.2,
  },
  subtitle: {
    fontSize: 15,
    lineHeight: 22,
    color: COLORS.textSecondary,
    maxWidth: 560,
  },
  formCard: {
    width: "100%",
    maxWidth: 680,
    alignSelf: "center",
    backgroundColor: COLORS.surfacePrimary,
    borderRadius: 24,
    borderWidth: 0.3,
    borderColor: COLORS.borderStrong,
    paddingHorizontal: isTabletLike ? 28 : 20,
    paddingVertical: isTabletLike ? 28 : 22,

    shadowColor: "#000",
    shadowOffset: { width: 0, height: isTabletLike ? 8 : 7 },
    shadowOpacity: 0.18,
    shadowRadius: isTabletLike ? 12 : 10,
    elevation: 3,
  },
  section: {
    marginBottom: 22,
  },
  sectionLabel: {
    fontSize: 16,
    fontWeight: "700",
    color: COLORS.textPrimary,
    marginBottom: 6,
  },
  sectionDescription: {
    fontSize: 14,
    lineHeight: 20,
    color: COLORS.textSecondary,
    marginBottom: 14,
  },
  methodRow: {
    flexDirection: "row",
  },
  methodButton: {
    flex: 1,
    minHeight: 88,
    borderRadius: 18,
    paddingHorizontal: 14,
    paddingVertical: 14,
    justifyContent: "space-between",
    borderWidth: 0.3,
  },
  methodButtonSpacing: {
    marginRight: 12,
  },
  methodButtonActive: {
    backgroundColor: COLORS.surfaceAccent,
    borderColor: COLORS.borderStrong,
  },
  methodButtonInactive: {
    backgroundColor: COLORS.surfaceSecondary,
    borderColor: COLORS.borderSoft,
  },
  methodTitle: {
    fontSize: 15,
    fontWeight: "700",
  },
  methodMeta: {
    fontSize: 13,
    fontWeight: "500",
  },
  methodTextActive: {
    color: COLORS.textPrimary,
  },
  methodTextInactive: {
    color: COLORS.textSecondary,
  },
  methodMetaActive: {
    color: "#dde2e8",
  },
  methodMetaInactive: {
    color: COLORS.textMuted,
  },
  amountInputWrapper: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: COLORS.surfaceSecondary,
    borderWidth: 0.3,
    borderColor: COLORS.borderStrong,
    borderRadius: 18,
    paddingHorizontal: 16,
    minHeight: 58,

    shadowColor: "#000",
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.12,
    shadowRadius: 8,
    elevation: 2,
  },
  amountPrefix: {
    fontSize: 20,
    fontWeight: "700",
    color: COLORS.textPrimary,
    marginRight: 8,
  },
  amountInput: {
    flex: 1,
    fontSize: 17,
    color: COLORS.textPrimary,
    paddingVertical: 0,
  },
  helperText: {
    marginTop: 10,
    fontSize: 13,
    lineHeight: 19,
    color: COLORS.textMuted,
  },
  summaryCard: {
    backgroundColor: COLORS.surfaceSecondary,
    borderRadius: 18,
    borderWidth: 0.3,
    borderColor: COLORS.borderSoft,
    paddingHorizontal: 16,
    paddingVertical: 14,
    marginTop: 2,
    marginBottom: 18,
  },
  summaryRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  summaryDivider: {
    height: 1,
    backgroundColor: "rgba(255,255,255,0.08)",
    marginVertical: 12,
  },
  summaryLabel: {
    fontSize: 14,
    color: COLORS.textSecondary,
  },
  summaryValue: {
    fontSize: 14,
    fontWeight: "700",
    color: COLORS.textPrimary,
  },
  summaryValueWarning: {
    color: COLORS.warning,
  },
  messageText: {
    fontSize: 14,
    fontWeight: "500",
    marginBottom: 14,
  },
  messageErrorText: {
    color: COLORS.danger,
  },
  messageSuccessText: {
    color: COLORS.success,
  },
  submitButton: {
    minHeight: 54,
    borderRadius: 18,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 0.3,
  },
  submitButtonActive: {
    backgroundColor: COLORS.surfaceAccent,
    borderColor: COLORS.borderStrong,

    shadowColor: "#000",
    shadowOffset: { width: 0, height: 7 },
    shadowOpacity: 0.16,
    shadowRadius: 10,
    elevation: 3,
  },
  submitButtonDisabled: {
    backgroundColor: "#4a525d",
    borderColor: COLORS.borderSoft,
    opacity: 0.72,
  },
  primaryButtonText: {
    color: COLORS.textPrimary,
    fontSize: 15,
    fontWeight: "700",
    letterSpacing: 0.2,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: COLORS.overlay,
    alignItems: "center",
    justifyContent: "center",
    padding: 24,
  },
  modalCard: {
    width: "100%",
    maxWidth: 360,
    backgroundColor: COLORS.surfacePrimary,
    borderRadius: 24,
    borderWidth: 0.3,
    borderColor: COLORS.borderStrong,
    paddingHorizontal: 24,
    paddingVertical: 28,
    alignItems: "center",

    shadowColor: "#000",
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.2,
    shadowRadius: 12,
    elevation: 4,
  },
  modalBadge: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: "#3f5149",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 16,
    borderWidth: 0.3,
    borderColor: COLORS.borderSoft,
  },
  modalBadgeText: {
    fontSize: 24,
    fontWeight: "700",
    color: COLORS.success,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: "700",
    color: COLORS.textPrimary,
    marginBottom: 10,
  },
  modalBody: {
    fontSize: 14,
    lineHeight: 21,
    color: COLORS.textSecondary,
    textAlign: "center",
    marginBottom: 20,
  },
  modalButton: {
    minWidth: 160,
    minHeight: 48,
    borderRadius: 16,
    backgroundColor: COLORS.surfaceAccent,
    borderWidth: 0.3,
    borderColor: COLORS.borderStrong,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 18,
  },
});