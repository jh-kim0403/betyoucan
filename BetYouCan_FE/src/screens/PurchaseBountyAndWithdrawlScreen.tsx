import React, { useContext, useMemo, useState } from "react";
import {
  ActivityIndicator,
  KeyboardAvoidingView,
  Modal,
  Platform,
  ScrollView,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import { useStripe } from "@stripe/stripe-react-native";
import AuthContext from "../context/AuthContext";
import { CommonActions, useNavigation } from "@react-navigation/native";
import { API_BASE_URL } from "../config/api";
import { styles } from "../styles/PurchaseBountyAndWithdrawlScreen.styles";

const MIN_BANK = 5;
const MIN_CARD = 10;

type Method = "bank" | "card";

export default function PurchaseBountyAndWithdrawlScreen() {
  const auth = useContext(AuthContext);
  const authFetch = auth?.authFetch;
  const token = auth?.token ?? null;
  const { initPaymentSheet, presentPaymentSheet } = useStripe();
  const navigation = useNavigation();

  const [amount, setAmount] = useState("");
  const [method, setMethod] = useState<Method>("bank");
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [showSuccessModal, setShowSuccessModal] = useState(false);

  const minAmount = method === "bank" ? MIN_BANK : MIN_CARD;

  const parsedAmount = useMemo(() => Number(amount), [amount]);
  const isValidAmount = Number.isFinite(parsedAmount) && parsedAmount > 0;
  const isBelowMinimum = isValidAmount && parsedAmount < minAmount;
  const helperText =
    method === "bank"
      ? "Bank payments support delayed settlement. Minimum purchase is $5."
      : "Debit card payments are processed instantly. Minimum purchase is $10.";

  const handlePurchase = async () => {
    if (!token) {
      setMessage("Missing access token. Please log in again.");
      return;
    }

    if (!isValidAmount) {
      setMessage("Enter a valid amount.");
      return;
    }

    if (parsedAmount < minAmount) {
      setMessage(`Minimum ${method} charge is $${minAmount}.`);
      return;
    }

    setIsLoading(true);
    setMessage(null);

    try {
      const response = await (authFetch ?? fetch)(
        `${API_BASE_URL}/payments/create-payment-intent`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            amount_cents: Math.round(parsedAmount * 100),
            method,
          }),
        }
      );

      if (!response.ok) {
        const err = await response.json().catch(() => null);
        throw new Error(err?.detail || "Failed to create payment intent");
      }

      const data = await response.json();
      const clientSecret = data?.client_secret;

      if (!clientSecret) {
        throw new Error("Missing payment intent client secret");
      }

      const init = await initPaymentSheet({
        merchantDisplayName: "DreamStudio",
        paymentIntentClientSecret: clientSecret,
        allowsDelayedPaymentMethods: method === "bank",
      });

      if (init.error) {
        throw new Error(init.error.message);
      }

      const present = await presentPaymentSheet();

      if (present.error) {
        throw new Error(present.error.message);
      }

      setAmount("");
      setMessage("Payment submitted.");
      setShowSuccessModal(true);
    } catch (error: any) {
      setMessage(error?.message ?? "Payment failed.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <KeyboardAvoidingView
        style={styles.screen}
        behavior={Platform.OS === "ios" ? "padding" : undefined}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          <View style={styles.container}>
            <View style={styles.headerBlock}>
              <Text style={styles.heading}>Purchase Bounty</Text>
              <Text style={styles.subtitle}>
                Add funds securely and choose the payment method that works best
                for you.
              </Text>
            </View>

            <View style={styles.formCard}>
              <View style={styles.section}>
                <Text style={styles.sectionLabel}>Payment method</Text>
                <Text style={styles.sectionDescription}>
                  Select how you want to fund your account.
                </Text>

                <View style={styles.methodRow}>
                  <TouchableOpacity
                    activeOpacity={0.9}
                    style={[
                      styles.methodButton,
                      styles.methodButtonSpacing,
                      method === "bank"
                        ? styles.methodButtonActive
                        : styles.methodButtonInactive,
                    ]}
                    onPress={() => setMethod("bank")}
                  >
                    <Text
                      style={[
                        styles.methodTitle,
                        method === "bank"
                          ? styles.methodTextActive
                          : styles.methodTextInactive,
                      ]}
                    >
                      Bank
                    </Text>
                    <Text
                      style={[
                        styles.methodMeta,
                        method === "bank"
                          ? styles.methodMetaActive
                          : styles.methodMetaInactive,
                      ]}
                    >
                      $5 minimum
                    </Text>
                  </TouchableOpacity>

                  <TouchableOpacity
                    activeOpacity={0.9}
                    style={[
                      styles.methodButton,
                      method === "card"
                        ? styles.methodButtonActive
                        : styles.methodButtonInactive,
                    ]}
                    onPress={() => setMethod("card")}
                  >
                    <Text
                      style={[
                        styles.methodTitle,
                        method === "card"
                          ? styles.methodTextActive
                          : styles.methodTextInactive,
                      ]}
                    >
                      Debit Card
                    </Text>
                    <Text
                      style={[
                        styles.methodMeta,
                        method === "card"
                          ? styles.methodMetaActive
                          : styles.methodMetaInactive,
                      ]}
                    >
                      $10 minimum
                    </Text>
                  </TouchableOpacity>
                </View>
              </View>

              <View style={styles.section}>
                <Text style={styles.sectionLabel}>Amount</Text>
                <Text style={styles.sectionDescription}>
                  Enter the dollar amount you want to add.
                </Text>

                <View style={styles.amountInputWrapper}>
                  <Text style={styles.amountPrefix}>$</Text>
                  <TextInput
                    value={amount}
                    onChangeText={setAmount}
                    placeholder={`Minimum ${minAmount}`}
                    placeholderTextColor="#8f98a3"
                    keyboardType="decimal-pad"
                    style={styles.amountInput}
                  />
                </View>

                <Text style={styles.helperText}>{helperText}</Text>
              </View>

              <View style={styles.summaryCard}>
                <View style={styles.summaryRow}>
                  <Text style={styles.summaryLabel}>Selected method</Text>
                  <Text style={styles.summaryValue}>
                    {method === "bank" ? "Bank" : "Debit Card"}
                  </Text>
                </View>

                <View style={styles.summaryDivider} />

                <View style={styles.summaryRow}>
                  <Text style={styles.summaryLabel}>Minimum required</Text>
                  <Text style={styles.summaryValue}>${minAmount}</Text>
                </View>

                {isValidAmount ? (
                  <>
                    <View style={styles.summaryDivider} />
                    <View style={styles.summaryRow}>
                      <Text style={styles.summaryLabel}>Entered amount</Text>
                      <Text
                        style={[
                          styles.summaryValue,
                          isBelowMinimum && styles.summaryValueWarning,
                        ]}
                      >
                        ${parsedAmount.toFixed(2)}
                      </Text>
                    </View>
                  </>
                ) : null}
              </View>

              {message ? (
                <Text
                  style={[
                    styles.messageText,
                    message === "Payment submitted."
                      ? styles.messageSuccessText
                      : styles.messageErrorText,
                  ]}
                >
                  {message}
                </Text>
              ) : null}

              <TouchableOpacity
                activeOpacity={0.9}
                style={[
                  styles.submitButton,
                  isLoading
                    ? styles.submitButtonDisabled
                    : styles.submitButtonActive,
                ]}
                onPress={handlePurchase}
                disabled={isLoading}
              >
                {isLoading ? (
                  <ActivityIndicator color="#F8FAFC" />
                ) : (
                  <Text style={styles.primaryButtonText}>Purchase Bounty</Text>
                )}
              </TouchableOpacity>
            </View>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>

      <Modal
        transparent
        visible={showSuccessModal}
        animationType="fade"
        onRequestClose={() => setShowSuccessModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalCard}>
            <View style={styles.modalBadge}>
              <Text style={styles.modalBadgeText}>✓</Text>
            </View>

            <Text style={styles.modalTitle}>Payment Success</Text>
            <Text style={styles.modalBody}>
              Your payment was submitted successfully and your balance will be
              updated shortly.
            </Text>

            <TouchableOpacity
              activeOpacity={0.9}
              style={styles.modalButton}
              onPress={() => {
                setShowSuccessModal(false);
                navigation.dispatch(
                  CommonActions.reset({
                    index: 0,
                    routes: [{ name: "Home" }],
                  })
                );
              }}
            >
              <Text style={styles.primaryButtonText}>Back to Home</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </>
  );
}