import { Dimensions, StyleSheet } from 'react-native';

const { width, height } = Dimensions.get('window');

const isTablet = width >= 768;
const contentWidth = Math.min(width - 44, 460);

const COLORS = {
  background: '#1f1f1f',
  surfaceInput: '#2a2f36',
  surfacePrimary: '#5d6976',
  surfaceSecondary: '#43505c',
  borderSoft: 'rgba(255, 255, 255, 0.30)',
  textPrimary: '#f3f4f6',
  textSecondary: '#aeb4bd',
  inputText: '#f3f4f6',
  placeholder: '#9aa3ad',
  icon: '#b3bac4',
  success: '#63d29a',
  danger: '#ff8c96',
};

export const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
    alignItems: 'center',
    paddingHorizontal: 22,
    paddingTop: isTablet ? height * 0.12 : height * 0.09,
  },

  contentWrapper: {
    width: contentWidth,
    maxWidth: '100%',
  },

  title: {
    fontSize: isTablet ? 34 : 30,
    fontWeight: '700',
    color: COLORS.textPrimary,
    textAlign: 'center',
    marginBottom: 70,
    letterSpacing: 0.2,
  },

  subtitle: {
    fontSize: isTablet ? 17 : 16,
    color: COLORS.textSecondary,
    textAlign: 'center',
    marginBottom: isTablet ? 26 : 22,
  },

  inputContainer: {
    width: '100%',
    paddingHorizontal: 0,
    marginBottom: -8,
  },

  inputInnerContainer: {
    minHeight: isTablet ? 60 : 54,
    flexDirection: 'row',
    alignItems: 'center',
    borderBottomWidth: 0,
    borderWidth: 0.3,
    borderColor: COLORS.borderSoft,
    borderRadius: isTablet ? 20 : 18,
    backgroundColor: COLORS.surfaceInput,
    paddingHorizontal: isTablet ? 18 : 16,

    shadowColor: '#000',
    shadowOffset: { width: 0, height: isTablet ? 8 : 7 },
    shadowOpacity: 0.18,
    shadowRadius: isTablet ? 12 : 10,
    elevation: 3,
  },

  primaryButtonContainer: {
    width: '100%',
    marginTop: 70,
    marginBottom: 10,
  },

  primaryButton: {
    width: '100%',
    minHeight: isTablet ? 60 : 54,
    borderRadius: isTablet ? 20 : 18,
    backgroundColor: COLORS.surfacePrimary,
    borderWidth: 0.3,
    borderColor: COLORS.borderSoft,
    justifyContent: 'center',
    alignItems: 'center',

    shadowColor: '#000',
    shadowOffset: { width: 0, height: isTablet ? 8 : 7 },
    shadowOpacity: 0.18,
    shadowRadius: isTablet ? 12 : 10,
    elevation: 3,
  },

  primaryButtonText: {
    fontWeight: '600',
    color: '#f3f4f6',
    fontSize: isTablet ? 18 : 17,
  },

  signUpButtonContainer: {
    width: '100%',
    marginTop: 2,
  },

  secondaryButton: {
    width: '100%',
    minHeight: isTablet ? 60 : 54,
    borderRadius: isTablet ? 20 : 18,
    backgroundColor: COLORS.surfaceSecondary,
    borderWidth: 0.3,
    borderColor: COLORS.borderSoft,
    justifyContent: 'center',
    alignItems: 'center',

    shadowColor: '#000',
    shadowOffset: { width: 0, height: isTablet ? 7 : 6 },
    shadowOpacity: 0.15,
    shadowRadius: isTablet ? 10 : 8,
    elevation: 2,
  },

  secondaryButtonText: {
    fontWeight: '600',
    color: '#dde2e8',
    fontSize: isTablet ? 18 : 17,
  },

  successText: {
    width: '100%',
    color: COLORS.success,
    marginTop: 10,
    marginBottom: 8,
    fontSize: isTablet ? 15 : 14,
    textAlign: 'center',
  },

  errorText: {
    width: '100%',
    color: COLORS.danger,
    marginTop: 1,
    marginBottom: 1,
    fontSize: isTablet ? 15 : 14,
    textAlign: 'center',
  },
});

export const iconProps = {
  email: {
    name: 'email' as const,
    size: isTablet ? 22 : 21,
    color: '#b3bac4',
  },
  password: {
    name: 'lock' as const,
    size: isTablet ? 22 : 21,
    color: '#b3bac4',
  },
};