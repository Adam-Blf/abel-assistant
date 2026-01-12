# =============================================================================
# PROGUARD RULES - Android Code Optimization & Security
# =============================================================================
# A.B.E.L. Project - Production build optimization rules
# =============================================================================

# Keep Expo and React Native classes
-keep class com.facebook.react.** { *; }
-keep class com.swmansion.** { *; }
-keep class expo.** { *; }

# Keep Supabase client
-keep class io.supabase.** { *; }

# Keep Reanimated
-keep class com.swmansion.reanimated.** { *; }

# Keep Hermes engine
-keep class com.facebook.hermes.** { *; }
-keep class com.facebook.jni.** { *; }

# Keep native modules
-keepclassmembers class * {
    @com.facebook.react.uimanager.annotations.ReactProp <methods>;
}

# Keep serializable classes
-keepclassmembers class * implements java.io.Serializable {
    static final long serialVersionUID;
    private static final java.io.ObjectStreamField[] serialPersistentFields;
    !static !transient <fields>;
    private void writeObject(java.io.ObjectOutputStream);
    private void readObject(java.io.ObjectInputStream);
    java.lang.Object writeReplace();
    java.lang.Object readResolve();
}

# Remove logging in production
-assumenosideeffects class android.util.Log {
    public static *** d(...);
    public static *** v(...);
    public static *** i(...);
}

# Preserve line numbers for crash reports
-keepattributes SourceFile,LineNumberTable
-renamesourcefileattribute SourceFile

# Don't warn about missing optional dependencies
-dontwarn org.bouncycastle.**
-dontwarn org.conscrypt.**
-dontwarn org.openjsse.**
