"""
A.B.E.L - Feature Manager
Manages all 100+ features of the ultimate assistant
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class FeatureCategory(str, Enum):
    """Feature categories"""
    COMMUNICATION = "communication"
    PRODUCTIVITY = "productivity"
    INFORMATION = "information"
    FINANCE = "finance"
    HEALTH = "health"
    ENTERTAINMENT = "entertainment"
    DEVELOPMENT = "development"
    UTILITIES = "utilities"
    SMART_HOME = "smart_home"
    LEARNING = "learning"
    SOCIAL = "social"
    TRAVEL = "travel"


@dataclass
class Feature:
    """Represents a feature"""
    id: str
    name: str
    description: str
    category: FeatureCategory
    enabled: bool = True
    requires_api_key: bool = False
    api_keys_needed: List[str] = None


# Complete list of 100+ features
ALL_FEATURES: List[Feature] = [
    # ========================================
    # COMMUNICATION & PRODUCTIVITY (1-20)
    # ========================================
    Feature("email_summarizer", "Email Summarizer", "Résume automatiquement les emails longs", FeatureCategory.COMMUNICATION),
    Feature("email_categorizer", "Email Categorizer", "Catégorise les emails automatiquement", FeatureCategory.COMMUNICATION),
    Feature("smart_reply", "Smart Reply", "Génère des réponses intelligentes aux emails", FeatureCategory.COMMUNICATION),
    Feature("meeting_scheduler", "Meeting Scheduler", "Planifie des réunions intelligemment", FeatureCategory.PRODUCTIVITY),
    Feature("meeting_notes", "Meeting Notes", "Génère des notes de réunion automatiquement", FeatureCategory.PRODUCTIVITY),
    Feature("task_manager", "Task Manager", "Gestion avancée des tâches avec priorités", FeatureCategory.PRODUCTIVITY),
    Feature("reminder_system", "Reminder System", "Système de rappels intelligent", FeatureCategory.PRODUCTIVITY),
    Feature("voice_notes", "Voice Notes", "Prend des notes vocales", FeatureCategory.PRODUCTIVITY),
    Feature("document_summarizer", "Document Summarizer", "Résume des documents PDF/Word", FeatureCategory.PRODUCTIVITY),
    Feature("pdf_analyzer", "PDF Analyzer", "Analyse et extrait des données de PDFs", FeatureCategory.PRODUCTIVITY),
    Feature("calendar_optimizer", "Calendar Optimizer", "Optimise ton emploi du temps", FeatureCategory.PRODUCTIVITY),
    Feature("focus_timer", "Focus Timer", "Pomodoro et timer de concentration", FeatureCategory.PRODUCTIVITY),
    Feature("habit_tracker", "Habit Tracker", "Suivi des habitudes quotidiennes", FeatureCategory.PRODUCTIVITY),
    Feature("goal_setter", "Goal Setter", "Définition et suivi d'objectifs", FeatureCategory.PRODUCTIVITY),
    Feature("project_planner", "Project Planner", "Planification de projets", FeatureCategory.PRODUCTIVITY),
    Feature("time_tracker", "Time Tracker", "Suivi du temps passé", FeatureCategory.PRODUCTIVITY),
    Feature("contact_manager", "Contact Manager", "Gestion avancée des contacts", FeatureCategory.COMMUNICATION),
    Feature("sms_handler", "SMS Handler", "Gestion des SMS", FeatureCategory.COMMUNICATION),
    Feature("call_log", "Call Log", "Historique et analyse des appels", FeatureCategory.COMMUNICATION),
    Feature("voice_transcriber", "Voice Transcriber", "Transcription vocale avancée", FeatureCategory.COMMUNICATION),

    # ========================================
    # INFORMATION & RESEARCH (21-40)
    # ========================================
    Feature("web_search", "Web Search", "Recherche web intégrée (Google, Bing, DuckDuckGo)", FeatureCategory.INFORMATION),
    Feature("news_aggregator", "News Aggregator", "Agrégation de news multi-sources", FeatureCategory.INFORMATION),
    Feature("wikipedia_lookup", "Wikipedia Lookup", "Recherche Wikipedia instantanée", FeatureCategory.INFORMATION),
    Feature("stock_tracker", "Stock Tracker", "Suivi des actions en temps réel", FeatureCategory.FINANCE),
    Feature("crypto_tracker", "Crypto Tracker", "Suivi des cryptomonnaies", FeatureCategory.FINANCE),
    Feature("weather_forecast", "Weather Forecast", "Prévisions météo détaillées", FeatureCategory.INFORMATION),
    Feature("flight_tracker", "Flight Tracker", "Suivi des vols en temps réel", FeatureCategory.TRAVEL),
    Feature("package_tracker", "Package Tracker", "Suivi des colis (UPS, FedEx, etc.)", FeatureCategory.UTILITIES),
    Feature("recipe_finder", "Recipe Finder", "Recherche de recettes", FeatureCategory.INFORMATION),
    Feature("movie_recommender", "Movie Recommender", "Recommandations de films", FeatureCategory.ENTERTAINMENT),
    Feature("tv_guide", "TV Guide", "Guide TV et recommandations séries", FeatureCategory.ENTERTAINMENT),
    Feature("book_recommender", "Book Recommender", "Recommandations de livres", FeatureCategory.ENTERTAINMENT),
    Feature("podcast_finder", "Podcast Finder", "Découverte de podcasts", FeatureCategory.ENTERTAINMENT),
    Feature("music_recommender", "Music Recommender", "Recommandations musicales (Spotify, Deezer)", FeatureCategory.ENTERTAINMENT),
    Feature("event_finder", "Event Finder", "Événements locaux", FeatureCategory.INFORMATION),
    Feature("restaurant_finder", "Restaurant Finder", "Restaurants à proximité", FeatureCategory.INFORMATION),
    Feature("place_finder", "Place Finder", "Recherche de lieux", FeatureCategory.INFORMATION),
    Feature("fact_checker", "Fact Checker", "Vérification des faits", FeatureCategory.INFORMATION),
    Feature("trend_analyzer", "Trend Analyzer", "Analyse des tendances", FeatureCategory.INFORMATION),
    Feature("research_assistant", "Research Assistant", "Assistant de recherche", FeatureCategory.INFORMATION),

    # ========================================
    # FINANCE & BUSINESS (41-55)
    # ========================================
    Feature("expense_tracker", "Expense Tracker", "Suivi des dépenses", FeatureCategory.FINANCE),
    Feature("budget_planner", "Budget Planner", "Planification budgétaire", FeatureCategory.FINANCE),
    Feature("bill_reminder", "Bill Reminder", "Rappels de factures", FeatureCategory.FINANCE),
    Feature("currency_converter", "Currency Converter", "Conversion de devises", FeatureCategory.FINANCE),
    Feature("investment_tracker", "Investment Tracker", "Suivi des investissements", FeatureCategory.FINANCE),
    Feature("crypto_portfolio", "Crypto Portfolio", "Portfolio crypto", FeatureCategory.FINANCE),
    Feature("tax_calculator", "Tax Calculator", "Calcul d'impôts", FeatureCategory.FINANCE),
    Feature("savings_goals", "Savings Goals", "Objectifs d'épargne", FeatureCategory.FINANCE),
    Feature("subscription_manager", "Subscription Manager", "Gestion des abonnements", FeatureCategory.FINANCE),
    Feature("price_comparator", "Price Comparator", "Comparateur de prix", FeatureCategory.FINANCE),
    Feature("invoice_generator", "Invoice Generator", "Génération de factures", FeatureCategory.FINANCE),
    Feature("receipt_scanner", "Receipt Scanner", "Scan de reçus", FeatureCategory.FINANCE),
    Feature("loan_calculator", "Loan Calculator", "Calculateur de prêts", FeatureCategory.FINANCE),
    Feature("tip_calculator", "Tip Calculator", "Calculateur de pourboire", FeatureCategory.FINANCE),
    Feature("split_bill", "Split Bill", "Partage de l'addition", FeatureCategory.FINANCE),

    # ========================================
    # HEALTH & FITNESS (56-70)
    # ========================================
    Feature("workout_generator", "Workout Generator", "Génération d'entraînements", FeatureCategory.HEALTH),
    Feature("calorie_counter", "Calorie Counter", "Compteur de calories", FeatureCategory.HEALTH),
    Feature("nutrition_advisor", "Nutrition Advisor", "Conseils nutritionnels", FeatureCategory.HEALTH),
    Feature("water_reminder", "Water Reminder", "Rappel d'hydratation", FeatureCategory.HEALTH),
    Feature("sleep_tracker", "Sleep Tracker", "Suivi du sommeil", FeatureCategory.HEALTH),
    Feature("meditation_guide", "Meditation Guide", "Guide de méditation", FeatureCategory.HEALTH),
    Feature("breathing_exercise", "Breathing Exercise", "Exercices de respiration", FeatureCategory.HEALTH),
    Feature("posture_reminder", "Posture Reminder", "Rappel de posture", FeatureCategory.HEALTH),
    Feature("eye_break", "Eye Break", "Pause pour les yeux (20-20-20)", FeatureCategory.HEALTH),
    Feature("step_counter", "Step Counter", "Compteur de pas", FeatureCategory.HEALTH),
    Feature("bmi_calculator", "BMI Calculator", "Calcul IMC", FeatureCategory.HEALTH),
    Feature("mood_tracker", "Mood Tracker", "Suivi de l'humeur", FeatureCategory.HEALTH),
    Feature("medication_reminder", "Medication Reminder", "Rappel de médicaments", FeatureCategory.HEALTH),
    Feature("symptom_checker", "Symptom Checker", "Vérificateur de symptômes", FeatureCategory.HEALTH),
    Feature("first_aid", "First Aid", "Guide premiers secours", FeatureCategory.HEALTH),

    # ========================================
    # DEVELOPMENT & TECH (71-85)
    # ========================================
    Feature("code_explainer", "Code Explainer", "Explication de code", FeatureCategory.DEVELOPMENT),
    Feature("code_reviewer", "Code Reviewer", "Review de code", FeatureCategory.DEVELOPMENT),
    Feature("bug_finder", "Bug Finder", "Détection de bugs", FeatureCategory.DEVELOPMENT),
    Feature("doc_generator", "Documentation Generator", "Génération de documentation", FeatureCategory.DEVELOPMENT),
    Feature("git_helper", "Git Helper", "Assistant Git", FeatureCategory.DEVELOPMENT),
    Feature("stackoverflow_search", "StackOverflow Search", "Recherche StackOverflow", FeatureCategory.DEVELOPMENT),
    Feature("package_search", "Package Search", "Recherche NPM/PyPI", FeatureCategory.DEVELOPMENT),
    Feature("api_tester", "API Tester", "Test d'APIs", FeatureCategory.DEVELOPMENT),
    Feature("json_formatter", "JSON Formatter", "Formatage JSON/XML", FeatureCategory.DEVELOPMENT),
    Feature("regex_helper", "Regex Helper", "Assistant expressions régulières", FeatureCategory.DEVELOPMENT),
    Feature("sql_helper", "SQL Helper", "Assistant SQL", FeatureCategory.DEVELOPMENT),
    Feature("docker_helper", "Docker Helper", "Assistant Docker", FeatureCategory.DEVELOPMENT),
    Feature("aws_helper", "AWS Helper", "Assistant AWS", FeatureCategory.DEVELOPMENT),
    Feature("linux_helper", "Linux Helper", "Assistant commandes Linux", FeatureCategory.DEVELOPMENT),
    Feature("security_scanner", "Security Scanner", "Scan de sécurité", FeatureCategory.DEVELOPMENT),

    # ========================================
    # UTILITIES & TOOLS (86-100)
    # ========================================
    Feature("unit_converter", "Unit Converter", "Conversion d'unités", FeatureCategory.UTILITIES),
    Feature("timezone_converter", "Timezone Converter", "Conversion fuseaux horaires", FeatureCategory.UTILITIES),
    Feature("calculator", "Calculator", "Calculatrice avancée", FeatureCategory.UTILITIES),
    Feature("password_generator", "Password Generator", "Génération de mots de passe", FeatureCategory.UTILITIES),
    Feature("qr_generator", "QR Generator", "Génération de QR codes", FeatureCategory.UTILITIES),
    Feature("url_shortener", "URL Shortener", "Raccourcisseur d'URLs", FeatureCategory.UTILITIES),
    Feature("file_converter", "File Converter", "Conversion de fichiers", FeatureCategory.UTILITIES),
    Feature("image_compressor", "Image Compressor", "Compression d'images", FeatureCategory.UTILITIES),
    Feature("color_picker", "Color Picker", "Sélecteur de couleurs", FeatureCategory.UTILITIES),
    Feature("text_analyzer", "Text Analyzer", "Analyse de texte", FeatureCategory.UTILITIES),
    Feature("translator", "Translator", "Traducteur multi-langues", FeatureCategory.UTILITIES),
    Feature("ocr_reader", "OCR Reader", "Lecture OCR", FeatureCategory.UTILITIES),
    Feature("speech_generator", "Speech Generator", "Synthèse vocale", FeatureCategory.UTILITIES),
    Feature("emoji_search", "Emoji Search", "Recherche d'emojis", FeatureCategory.UTILITIES),
    Feature("lorem_generator", "Lorem Generator", "Génération de Lorem Ipsum", FeatureCategory.UTILITIES),

    # ========================================
    # BONUS FEATURES (101-120)
    # ========================================
    Feature("daily_briefing", "Daily Briefing", "Résumé quotidien personnalisé", FeatureCategory.PRODUCTIVITY),
    Feature("birthday_reminder", "Birthday Reminder", "Rappels d'anniversaires", FeatureCategory.SOCIAL),
    Feature("gift_suggester", "Gift Suggester", "Suggestions de cadeaux", FeatureCategory.SOCIAL),
    Feature("travel_planner", "Travel Planner", "Planification de voyages", FeatureCategory.TRAVEL),
    Feature("packing_list", "Packing List", "Listes de bagages", FeatureCategory.TRAVEL),
    Feature("language_learner", "Language Learner", "Apprentissage de langues", FeatureCategory.LEARNING),
    Feature("flashcards", "Flashcards", "Système de flashcards", FeatureCategory.LEARNING),
    Feature("quiz_generator", "Quiz Generator", "Génération de quiz", FeatureCategory.LEARNING),
    Feature("random_facts", "Random Facts", "Faits aléatoires", FeatureCategory.ENTERTAINMENT),
    Feature("joke_teller", "Joke Teller", "Blagues", FeatureCategory.ENTERTAINMENT),
    Feature("quote_of_day", "Quote of Day", "Citation du jour", FeatureCategory.ENTERTAINMENT),
    Feature("meme_generator", "Meme Generator", "Génération de mèmes", FeatureCategory.ENTERTAINMENT),
    Feature("game_recommender", "Game Recommender", "Recommandations de jeux", FeatureCategory.ENTERTAINMENT),
    Feature("anime_tracker", "Anime Tracker", "Suivi des animes", FeatureCategory.ENTERTAINMENT),
    Feature("manga_reader", "Manga Reader", "Lecteur de mangas", FeatureCategory.ENTERTAINMENT),
    Feature("smart_home", "Smart Home", "Contrôle maison connectée", FeatureCategory.SMART_HOME),
    Feature("iot_monitor", "IoT Monitor", "Monitoring IoT", FeatureCategory.SMART_HOME),
    Feature("energy_tracker", "Energy Tracker", "Suivi consommation énergie", FeatureCategory.SMART_HOME),
    Feature("security_cam", "Security Cam", "Caméras de sécurité", FeatureCategory.SMART_HOME),
    Feature("voice_commands", "Voice Commands", "Commandes vocales avancées", FeatureCategory.SMART_HOME),
]


class FeatureManager:
    """Manages all features"""

    def __init__(self):
        self.features = {f.id: f for f in ALL_FEATURES}

    def get_all(self) -> List[Feature]:
        return ALL_FEATURES

    def get_by_category(self, category: FeatureCategory) -> List[Feature]:
        return [f for f in ALL_FEATURES if f.category == category]

    def get_enabled(self) -> List[Feature]:
        return [f for f in ALL_FEATURES if f.enabled]

    def enable(self, feature_id: str) -> bool:
        if feature_id in self.features:
            self.features[feature_id].enabled = True
            return True
        return False

    def disable(self, feature_id: str) -> bool:
        if feature_id in self.features:
            self.features[feature_id].enabled = False
            return True
        return False

    def search(self, query: str) -> List[Feature]:
        query_lower = query.lower()
        return [
            f for f in ALL_FEATURES
            if query_lower in f.name.lower() or query_lower in f.description.lower()
        ]

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_features": len(ALL_FEATURES),
            "enabled": len([f for f in ALL_FEATURES if f.enabled]),
            "by_category": {
                cat.value: len([f for f in ALL_FEATURES if f.category == cat])
                for cat in FeatureCategory
            }
        }
