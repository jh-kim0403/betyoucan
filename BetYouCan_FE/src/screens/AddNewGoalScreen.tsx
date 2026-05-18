import React, { useContext, useEffect, useMemo, useState, useCallback } from "react";
import {
  ActivityIndicator,
  Modal,
  Platform,
  ScrollView,
  Text,
  TextInput,
  Pressable,
  View,
} from "react-native";
import AuthContext from "../context/AuthContext";
import DateTimePicker from "@react-native-community/datetimepicker";
import { CommonActions, useNavigation } from "@react-navigation/native";
import { API_BASE_URL } from "../config/api";
import { styles } from "../styles/AddNewGoalScreen.styles";

type GoalType = {
  id: string;
  name: string;
  description?: string;
  question_count?: number;
};

type BibleBook = {
  name: string;
  chapters: number;
};

const BIBLE_BOOKS: BibleBook[] = [
  { name: "Genesis", chapters: 50 },
  { name: "Exodus", chapters: 40 },
  { name: "Leviticus", chapters: 27 },
  { name: "Numbers", chapters: 36 },
  { name: "Deuteronomy", chapters: 34 },
  { name: "Joshua", chapters: 24 },
  { name: "Judges", chapters: 21 },
  { name: "Ruth", chapters: 4 },
  { name: "1 Samuel", chapters: 31 },
  { name: "2 Samuel", chapters: 24 },
  { name: "1 Kings", chapters: 22 },
  { name: "2 Kings", chapters: 25 },
  { name: "1 Chronicles", chapters: 29 },
  { name: "2 Chronicles", chapters: 36 },
  { name: "Ezra", chapters: 10 },
  { name: "Nehemiah", chapters: 13 },
  { name: "Esther", chapters: 10 },
  { name: "Job", chapters: 42 },
  { name: "Psalms", chapters: 150 },
  { name: "Proverbs", chapters: 31 },
  { name: "Ecclesiastes", chapters: 12 },
  { name: "Song of Solomon", chapters: 8 },
  { name: "Isaiah", chapters: 66 },
  { name: "Jeremiah", chapters: 52 },
  { name: "Lamentations", chapters: 5 },
  { name: "Ezekiel", chapters: 48 },
  { name: "Daniel", chapters: 12 },
  { name: "Hosea", chapters: 14 },
  { name: "Joel", chapters: 3 },
  { name: "Amos", chapters: 9 },
  { name: "Obadiah", chapters: 1 },
  { name: "Jonah", chapters: 4 },
  { name: "Micah", chapters: 7 },
  { name: "Nahum", chapters: 3 },
  { name: "Habakkuk", chapters: 3 },
  { name: "Zephaniah", chapters: 3 },
  { name: "Haggai", chapters: 2 },
  { name: "Zechariah", chapters: 14 },
  { name: "Malachi", chapters: 4 },
  { name: "Matthew", chapters: 28 },
  { name: "Mark", chapters: 16 },
  { name: "Luke", chapters: 24 },
  { name: "John", chapters: 21 },
  { name: "Acts", chapters: 28 },
  { name: "Romans", chapters: 16 },
  { name: "1 Corinthians", chapters: 16 },
  { name: "2 Corinthians", chapters: 13 },
  { name: "Galatians", chapters: 6 },
  { name: "Ephesians", chapters: 6 },
  { name: "Philippians", chapters: 4 },
  { name: "Colossians", chapters: 4 },
  { name: "1 Thessalonians", chapters: 5 },
  { name: "2 Thessalonians", chapters: 3 },
  { name: "1 Timothy", chapters: 6 },
  { name: "2 Timothy", chapters: 4 },
  { name: "Titus", chapters: 3 },
  { name: "Philemon", chapters: 1 },
  { name: "Hebrews", chapters: 13 },
  { name: "James", chapters: 5 },
  { name: "1 Peter", chapters: 5 },
  { name: "2 Peter", chapters: 3 },
  { name: "1 John", chapters: 5 },
  { name: "2 John", chapters: 1 },
  { name: "3 John", chapters: 1 },
  { name: "Jude", chapters: 1 },
  { name: "Revelation", chapters: 22 },
];

const setEndOfDay = (date: Date) =>
  new Date(date.getFullYear(), date.getMonth(), date.getDate(), 23, 59, 0, 0);

const formatDeadlineDisplay = (date: Date | null) => {
  if (!date) return "Select deadline date";

  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "2-digit",
    year: "numeric",
  }).format(date);
};

export default function AddNewGoalScreen() {
  const auth = useContext(AuthContext);
  const token = auth?.token ?? null;
  const authFetch = auth?.authFetch;
  const navigation = useNavigation();

  const [goalTypes, setGoalTypes] = useState<GoalType[]>([]);
  const [goalTypeError, setGoalTypeError] = useState<string | null>(null);
  const [isGoalTypesLoading, setIsGoalTypesLoading] = useState(false);
  const [isGoalTypeOpen, setIsGoalTypeOpen] = useState(false);
  const [selectedGoalType, setSelectedGoalType] = useState<GoalType | null>(null);

  const [isBibleBookOpen, setIsBibleBookOpen] = useState(false);
  const [selectedBibleBook, setSelectedBibleBook] = useState<BibleBook | null>(null);
  const [fromChapter, setFromChapter] = useState("1");
  const [toChapter, setToChapter] = useState("1");

  const [deadline, setDeadline] = useState<Date | null>(null);
  const [showDeadlinePicker, setShowDeadlinePicker] = useState(false);
  const [deadlineError, setDeadlineError] = useState<string | null>(null);

  const [title, setTitle] = useState("");
  const [bountyAmount, setBountyAmount] = useState("");
  const [notificationTone, setNotificationTone] = useState<'harsh' | 'normal' | 'soft'>('harsh');
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchGoalTypes = useCallback(async () => {
    if (!token) return;

    setIsGoalTypesLoading(true);
    setGoalTypeError(null);

    try {
      const response = await (authFetch ?? fetch)(`${API_BASE_URL}/goals/goaltypes`, {
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Failed to load goal types");
      }

      const data = await response.json();
      setGoalTypes(Array.isArray(data) ? data : []);
    } catch (error: any) {
      setGoalTypeError("Failed to load goal types");
    } finally {
      setIsGoalTypesLoading(false);
    }
  }, [token, authFetch]);

  useEffect(() => {
    void fetchGoalTypes();
  }, [fetchGoalTypes]);

  const isBibleGoal = useMemo(() => {
    const name = selectedGoalType?.name?.toLowerCase() ?? "";
    return name.includes("bible");
  }, [selectedGoalType]);

  const maxChapters = selectedBibleBook?.chapters ?? 0;

  useEffect(() => {
    if (!selectedBibleBook) return;
    setFromChapter("1");
    setToChapter("1");
  }, [selectedBibleBook]);

  const clampChapter = (value: string) => {
    const numeric = parseInt(value || "0", 10);
    if (!numeric || numeric < 1) return "1";
    if (maxChapters && numeric > maxChapters) return String(maxChapters);
    return String(numeric);
  };

  const handleFromChange = (value: string) => {
    const next = clampChapter(value.replace(/[^0-9]/g, ""));
    setFromChapter(next);

    const nextNum = parseInt(next, 10);
    const toNum = parseInt(toChapter || "1", 10);

    if (toNum < nextNum) {
      setToChapter(String(nextNum));
    }

    if (submitError) setSubmitError(null);
  };

  const handleToChange = (value: string) => {
    const next = clampChapter(value.replace(/[^0-9]/g, ""));
    const nextNum = parseInt(next, 10);
    const fromNum = parseInt(fromChapter || "1", 10);

    if (nextNum < fromNum) {
      setToChapter(String(fromNum));
    } else {
      setToChapter(next);
    }

    if (submitError) setSubmitError(null);
  };

  const validateDeadline = (date: Date) => {
    const now = new Date();
    const selected = new Date(date);

    if (selected < now) {
      setDeadlineError("Deadline must be today or later");
      return false;
    }

    setDeadlineError(null);
    return true;
  };

  const handleSubmit = async () => {
    if (!token) {
      setSubmitError("Missing access token. Please log in again.");
      return;
    }

    if (!selectedGoalType) {
      setSubmitError("Select a goal type.");
      return;
    }

    if (!title.trim()) {
      setSubmitError("Enter a title.");
      return;
    }

    if (!deadline) {
      setSubmitError("Select a deadline.");
      return;
    }

    if (!validateDeadline(deadline)) {
      setSubmitError("Deadline must be today or later.");
      return;
    }


    if (!bountyAmount.trim() || Number.isNaN(Number(bountyAmount))) {
      setSubmitError("Enter a valid bounty amount.");
      return;
    }

    if (isBibleGoal && !selectedBibleBook) {
      setSubmitError("Select a bible book.");
      return;
    }

    setSubmitError(null);
    setIsSubmitting(true);

    const userInput =
      isBibleGoal && selectedBibleBook
        ? `Read ${selectedBibleBook.name} ${fromChapter}-${toChapter}`
        : "";

    try {
      const response = await (authFetch ?? fetch)(`${API_BASE_URL}/goals/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          goal_type_id: selectedGoalType.id,
          title: title.trim(),
          user_input: userInput,
          bounty_amount: Number(bountyAmount),
          deadline: deadline.toISOString(),
          notification_tone: notificationTone,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to create goal");
      }

      setTitle("");
      setNotificationTone('harsh');
      setDeadline(null);
      setSelectedBibleBook(null);
      setFromChapter("1");
      setToChapter("1");

      navigation.dispatch(
        CommonActions.reset({
          index: 0,
          routes: [{ name: "Home" }],
        })
      );
    } catch (error: any) {
      setSubmitError("Failed to create goal");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <View style={styles.container}>
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
        keyboardShouldPersistTaps="handled"
      >
        <View style={styles.contentWrapper}>
          <Text style={styles.heading}>Add New Goal</Text>
          <Text style={styles.subtitle}>Set a clear goal and deadline.</Text>

          <View style={styles.formCard}>
            <View style={styles.formSection}>
              <Text style={styles.inputLabel}>Goal Type</Text>

              <View style={styles.inlineSelector}>
                <Pressable
                  onPress={() => setIsGoalTypeOpen((prev) => !prev)}
                  style={styles.selectorToggle}
                >
                  <Text style={styles.selectorLabel}>
                    {selectedGoalType?.name || "Select goal type"}
                  </Text>
                  <Text style={styles.selectorToggleText}>
                    {isGoalTypeOpen ? "Hide" : "Show"}
                  </Text>
                </Pressable>

                {isGoalTypeOpen ? (
                  <View style={styles.selectorList}>
                    {isGoalTypesLoading ? (
                      <View style={styles.loadingRow}>
                        <ActivityIndicator size="small" color="#aeb4bd" />
                      </View>
                    ) : null}

                    {goalTypeError ? (
                      <Text style={[styles.errorText, styles.selectorError]}>{goalTypeError}</Text>
                    ) : null}

                    {goalTypes.map((type) => (
                      <Pressable
                        key={type.id}
                        onPress={() => {
                          setSelectedGoalType(type);
                          setIsGoalTypeOpen(false);
                          setSubmitError(null);
                        }}
                        style={styles.selectorItem}
                      >
                        <Text style={styles.selectorItemTitle}>{type.name}</Text>
                        {type.description ? (
                          <Text style={styles.selectorItemDescription}>{type.description}</Text>
                        ) : null}
                      </Pressable>
                    ))}
                  </View>
                ) : null}
              </View>
            </View>

            {isBibleGoal ? (
              <>
                <View style={styles.sectionDivider} />

                <View style={styles.formSection}>
                  <Text style={styles.sectionTitle}>Read the Bible</Text>

                  <View style={styles.inlineSelector}>
                    <Pressable
                      onPress={() => setIsBibleBookOpen((prev) => !prev)}
                      style={styles.selectorToggle}
                    >
                      <Text style={styles.selectorLabel}>
                        {selectedBibleBook?.name || "Select bible book"}
                      </Text>
                      <Text style={styles.selectorToggleText}>
                        {isBibleBookOpen ? "Hide" : "Show"}
                      </Text>
                    </Pressable>

                    {isBibleBookOpen ? (
                      <View style={styles.selectorList}>
                        {BIBLE_BOOKS.map((book) => (
                          <Pressable
                            key={book.name}
                            onPress={() => {
                              setSelectedBibleBook(book);
                              setIsBibleBookOpen(false);
                              setSubmitError(null);
                            }}
                            style={styles.selectorItem}
                          >
                            <Text style={styles.selectorItemTitle}>
                              {book.name} ({book.chapters} chapters)
                            </Text>
                          </Pressable>
                        ))}
                      </View>
                    ) : null}
                  </View>

                  <View style={styles.chapterRow}>
                    <View style={styles.chapterField}>
                      <Text style={styles.inputLabel}>From</Text>
                      <TextInput
                        value={fromChapter}
                        onChangeText={handleFromChange}
                        keyboardType="number-pad"
                        placeholder="1"
                        placeholderTextColor="#9aa3ad"
                        style={styles.input}
                      />
                    </View>

                    <View style={styles.chapterField}>
                      <Text style={styles.inputLabel}>To</Text>
                      <TextInput
                        value={toChapter}
                        onChangeText={handleToChange}
                        keyboardType="number-pad"
                        placeholder="1"
                        placeholderTextColor="#9aa3ad"
                        style={styles.input}
                      />
                    </View>
                  </View>

                  {selectedBibleBook ? (
                    <Text style={styles.helperText}>
                      Chapters range: 1 to {selectedBibleBook.chapters}
                    </Text>
                  ) : null}
                </View>
              </>
            ) : null}

            <View style={styles.sectionDivider} />

            <View style={styles.formSection}>
              <Text style={styles.inputLabel}>Deadline</Text>

              <Pressable
                onPress={() => setShowDeadlinePicker(true)}
                style={styles.input}
              >
                <Text style={deadline ? styles.inputText : styles.placeholderText}>
                  {formatDeadlineDisplay(deadline)}
                </Text>
              </Pressable>

              <Text style={styles.helperText}>Time is automatically set to 11:59 PM.</Text>

              {showDeadlinePicker ? (
                <DateTimePicker
                  value={deadline ?? setEndOfDay(new Date())}
                  mode="date"
                  minimumDate={new Date()}
                  display="default"
                  onChange={(event, selectedDate) => {
                    if (Platform.OS === "android" && event?.type === "dismissed") {
                      setShowDeadlinePicker(false);
                      return;
                    }

                    if (selectedDate) {
                      const next = setEndOfDay(selectedDate);
                      setDeadline(next);
                      validateDeadline(next);
                      setSubmitError(null);
                    }

                    setShowDeadlinePicker(false);
                  }}
                />
              ) : null}

              {deadlineError ? (
                <Text style={styles.inlineErrorText}>{deadlineError}</Text>
              ) : null}
            </View>

            <View style={styles.sectionDivider} />

            <View style={styles.formSection}>
              <Text style={styles.inputLabel}>Notification Tone</Text>
              <View style={{ flexDirection: 'row', gap: 8 }}>
                {(['harsh', 'normal', 'soft'] as const).map((tone) => (
                  <Pressable
                    key={tone}
                    onPress={() => setNotificationTone(tone)}
                    style={[
                      styles.selectorItem,
                      { flex: 1, alignItems: 'center' },
                      notificationTone === tone && { borderColor: '#aeb4bd', borderWidth: 1 },
                    ]}
                  >
                    <Text style={styles.selectorItemTitle}>
                      {tone.charAt(0).toUpperCase() + tone.slice(1)}
                    </Text>
                  </Pressable>
                ))}
              </View>
            </View>

            <View style={styles.sectionDivider} />

            <View style={styles.formSection}>
              <Text style={styles.inputLabel}>Title</Text>
              <TextInput
                value={title}
                onChangeText={(text) => {
                  setTitle(text);
                  if (submitError) setSubmitError(null);
                }}
                placeholder="Goal title"
                placeholderTextColor="#9aa3ad"
                style={styles.input}
              />
            </View>

            <View style={styles.sectionDivider} />

            <View style={styles.formSection}>
              <Text style={styles.inputLabel}>Bounty Amount</Text>
              <TextInput
                value={bountyAmount}
                onChangeText={(text) => {
                  setBountyAmount(text);
                  if (submitError) setSubmitError(null);
                }}
                placeholder="100"
                placeholderTextColor="#9aa3ad"
                keyboardType="number-pad"
                style={styles.input}
              />
            </View>

          </View>

          {submitError ? <Text style={styles.submitError}>{submitError}</Text> : null}

          <Pressable
            style={[
              styles.submitButton,
              isSubmitting ? styles.submitButtonDisabled : styles.submitButtonActive,
            ]}
            disabled={isSubmitting}
            onPress={handleSubmit}
          >
            <Text style={styles.submitButtonText}>Create Goal</Text>
          </Pressable>
        </View>
      </ScrollView>
    </View>
  );
}