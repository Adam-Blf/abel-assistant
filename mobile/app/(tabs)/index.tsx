/**
 * =============================================================================
 * (TABS)/INDEX.TSX - Chat Screen
 * =============================================================================
 * A.B.E.L. Project - Main chat interface with Gemini AI
 * =============================================================================
 */

import { useState, useCallback, useRef } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";

import { useAuth } from "@contexts/AuthContext";
import { apiClient } from "@services/api/client";
import { colors } from "@theme/colors";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export default function ChatScreen() {
  const { user } = useAuth();
  const flatListRef = useRef<FlatList>(null);

  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content: `Bonjour${user?.name ? ` ${user.name}` : ""} ! Je suis A.B.E.L., votre assistant IA personnel. Comment puis-je vous aider aujourd'hui ?`,
      timestamp: new Date(),
    },
  ]);
  const [inputText, setInputText] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  /**
   * Send message to API
   */
  const sendMessage = useCallback(async () => {
    if (!inputText.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: inputText.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputText("");
    setIsLoading(true);

    try {
      // Prepare history for API
      const history = messages.slice(-10).map((msg) => ({
        role: msg.role,
        content: msg.content,
      }));

      const response = await apiClient.post<{
        message: string;
        role: string;
        timestamp: string;
        model: string;
      }>("/chat/", {
        message: userMessage.content,
        history,
      });

      if (response.data) {
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: response.data.message,
          timestamp: new Date(response.data.timestamp),
        };

        setMessages((prev) => [...prev, assistantMessage]);
      } else {
        // Error response
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: "Désolé, une erreur s'est produite. Veuillez réessayer.",
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error("[Chat] Send error:", error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "Erreur de connexion. Vérifiez votre connexion internet.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [inputText, messages, isLoading]);

  /**
   * Render message bubble
   */
  const renderMessage = ({ item }: { item: Message }) => {
    const isUser = item.role === "user";

    return (
      <View
        style={{
          alignSelf: isUser ? "flex-end" : "flex-start",
          maxWidth: "80%",
          marginVertical: 4,
          marginHorizontal: 16,
        }}
      >
        {isUser ? (
          <LinearGradient
            colors={[colors.neon.cyan, colors.neon.purple]}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 0 }}
            style={{
              padding: 12,
              borderRadius: 16,
              borderBottomRightRadius: 4,
            }}
          >
            <Text style={{ color: colors.background.primary, fontSize: 15 }}>
              {item.content}
            </Text>
          </LinearGradient>
        ) : (
          <View
            style={{
              backgroundColor: colors.background.card,
              padding: 12,
              borderRadius: 16,
              borderBottomLeftRadius: 4,
              borderWidth: 1,
              borderColor: colors.border.default,
            }}
          >
            <Text style={{ color: colors.text.primary, fontSize: 15 }}>
              {item.content}
            </Text>
          </View>
        )}
        <Text
          style={{
            color: colors.text.muted,
            fontSize: 10,
            marginTop: 4,
            alignSelf: isUser ? "flex-end" : "flex-start",
          }}
        >
          {item.timestamp.toLocaleTimeString("fr-FR", {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </Text>
      </View>
    );
  };

  return (
    <SafeAreaView
      style={{ flex: 1, backgroundColor: colors.background.primary }}
      edges={["top"]}
    >
      {/* Header */}
      <View
        style={{
          flexDirection: "row",
          alignItems: "center",
          justifyContent: "space-between",
          paddingHorizontal: 16,
          paddingVertical: 12,
          borderBottomWidth: 1,
          borderBottomColor: colors.border.default,
        }}
      >
        <View style={{ flexDirection: "row", alignItems: "center" }}>
          <View
            style={{
              width: 40,
              height: 40,
              borderRadius: 20,
              backgroundColor: colors.background.card,
              borderWidth: 2,
              borderColor: colors.neon.cyan,
              justifyContent: "center",
              alignItems: "center",
            }}
          >
            <Ionicons name="sparkles" size={20} color={colors.neon.cyan} />
          </View>
          <View style={{ marginLeft: 12 }}>
            <Text
              style={{
                color: colors.text.primary,
                fontSize: 18,
                fontWeight: "bold",
              }}
            >
              A.B.E.L.
            </Text>
            <Text style={{ color: colors.neon.green, fontSize: 12 }}>
              En ligne
            </Text>
          </View>
        </View>

        <TouchableOpacity
          style={{
            width: 40,
            height: 40,
            borderRadius: 20,
            backgroundColor: colors.background.card,
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          <Ionicons name="ellipsis-vertical" size={20} color={colors.text.secondary} />
        </TouchableOpacity>
      </View>

      {/* Messages */}
      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : "height"}
        style={{ flex: 1 }}
        keyboardVerticalOffset={90}
      >
        <FlatList
          ref={flatListRef}
          data={messages}
          renderItem={renderMessage}
          keyExtractor={(item) => item.id}
          contentContainerStyle={{ paddingVertical: 16 }}
          onContentSizeChange={() =>
            flatListRef.current?.scrollToEnd({ animated: true })
          }
        />

        {/* Loading indicator */}
        {isLoading && (
          <View
            style={{
              flexDirection: "row",
              alignItems: "center",
              paddingHorizontal: 20,
              paddingBottom: 8,
            }}
          >
            <ActivityIndicator size="small" color={colors.neon.cyan} />
            <Text style={{ color: colors.text.muted, marginLeft: 8, fontSize: 12 }}>
              A.B.E.L. réfléchit...
            </Text>
          </View>
        )}

        {/* Input */}
        <View
          style={{
            flexDirection: "row",
            alignItems: "flex-end",
            paddingHorizontal: 16,
            paddingVertical: 12,
            borderTopWidth: 1,
            borderTopColor: colors.border.default,
            backgroundColor: colors.background.secondary,
          }}
        >
          <View
            style={{
              flex: 1,
              flexDirection: "row",
              alignItems: "flex-end",
              backgroundColor: colors.background.card,
              borderRadius: 24,
              borderWidth: 1,
              borderColor: colors.border.default,
              paddingHorizontal: 16,
              paddingVertical: 8,
              marginRight: 12,
            }}
          >
            <TextInput
              style={{
                flex: 1,
                color: colors.text.primary,
                fontSize: 15,
                maxHeight: 100,
              }}
              placeholder="Écrivez votre message..."
              placeholderTextColor={colors.text.muted}
              value={inputText}
              onChangeText={setInputText}
              multiline
              returnKeyType="send"
              onSubmitEditing={sendMessage}
            />
          </View>

          <TouchableOpacity
            onPress={sendMessage}
            disabled={!inputText.trim() || isLoading}
            style={{
              width: 48,
              height: 48,
              borderRadius: 24,
              overflow: "hidden",
            }}
          >
            <LinearGradient
              colors={
                inputText.trim() && !isLoading
                  ? [colors.neon.cyan, colors.neon.purple]
                  : [colors.background.card, colors.background.card]
              }
              style={{
                width: "100%",
                height: "100%",
                justifyContent: "center",
                alignItems: "center",
              }}
            >
              <Ionicons
                name="send"
                size={20}
                color={
                  inputText.trim() && !isLoading
                    ? colors.background.primary
                    : colors.text.muted
                }
              />
            </LinearGradient>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
