import json
import os
import random
import re
from abc import ABC, abstractmethod
from typing import *

class GameDataLoader:
    @staticmethod
    def load_json(file_name: str) -> Dict:
        """Load JSON data from file"""
        try:
            with open(file_name, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Game data file {file_name} not found")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in {file_name}")

# Game Services
class CharacterService:
    def __init__(self, data_file: str = 'characters.json'):
        data = GameDataLoader.load_json(data_file)
        self.characters = data.get('characters', {})

    def get_character_info(self, name: str) -> dict:
        return self.characters.get(name.capitalize(), {})

    def get_character_stats(self, name: str) -> str:
        """Format character stats for display"""
        char = self.get_character_info(name)
        if not char:
            return f"Character '{name}' not found"

        stats = [
            f"=== {name.upper()} ===",
            f"Type: {char['type']} | HP: {char['hp']}",
            "",
            f"ATTACK: {char['attack']['name']}",
            f"- {char['attack']['description']}",
            f"- Damage: {char['attack']['damage']} HP",
            "",
            f"DEFENSE: {char['defense']['name']}",
            f"- {char['defense']['description']}",
            f"- Base: {char['defense']['base']} HP | Boost: {char['defense']['boost']} HP",
            "",
            f"SPECIAL: {char['special']['name']} (Cooldown: {char['special']['cooldown']} turns)",
            f"- {char['special']['description']}",
            "- Effects: " + ", ".join(char['special']['effects']),
            "",
            f"DESCRIPTION: {char['description']}"
        ]
        return "\n".join(stats)


class ActionService:
    def __init__(self, data_file: str = 'game_config.json'):
        data = GameDataLoader.load_json(data_file)
        self.actions = data.get('actions', {})

    def get_action_info(self, action: str) -> Dict:
        """Get action description and effects"""
        return self.actions.get(action.capitalize(), {})

    def format_action_info(self, action: str) -> str:
        """Format action information for display"""
        info = self.get_action_info(action)
        if not info:
            return f"Action '{action}' not found"
        return (
            f"=== {action.upper()} ===\n"
            f"Description: {info['description']}\n"
            f"Effect: {info['effect']}"
        )


class GameStrategyService:
    def __init__(self, data_file: str = 'game_config.json'):
        data = GameDataLoader.load_json(data_file)
        self.strategies = data.get('strategies', [])

    def get_random_strategy(self) -> str:
        """Get a random strategy tip"""
        return random.choice(self.strategies) if self.strategies else "No strategies available"

# LiveAgentService: class
class LiveAgentService:
    # Purpose: Backend service that handles connections to live customer service agents
    def connect(self) -> str:
        LiveAgentNotifier.notify_agents("Customer requested live agent")
        return ResponseFactory.get_random_response("live_agent_connect")

# region Adapter Pattern
# endregion

# BackendManager: class
class BackendManager:
    def __init__(self) -> None:
        self.character_service = CharacterService()
        self.action_service = ActionService()
        self.strategy_service = GameStrategyService()

    def process_request(self, request_type: str, *args) -> str:
        if request_type == "character":
            return self._format_character_response(args[0])
        elif request_type == "action":
            return self._format_action_response(args[0])
        elif request_type == "advice":
            return self.strategy_service.get_advice()
        return "Request not supported."

    def _format_character_response(self, name: str) -> str:
        info = self.character_service.get_character_info(name)
        return f"{name}: {info['description']} Special: {info['special']}" if info else "Character not found"

    def _format_action_response(self, action: str) -> str:
        info = self.action_service.get_action_info(action)
        return f"{action}: {info['description']} Effect: {info['effect']}" if info else "Action not found"

# SessionManager: class
class SessionManager:
    # Purpose: Maintains the conversation state between the user and chatbot in storage 
    # Effect: Stores and retrieves the sessions' data like the order ID, conversation history, and future flags
    def __init__(self):
        self.sessions = {}
    
    # Purpose: Retrieves a value from the session storage using the given key
    def get(self, key: str, default=None):
        return self.sessions.get(key, default)
    
    # Purpose: Stores a value in the session storage using the given key and its value
    def set(self, key: str, value) -> None:
        self.sessions[key] = value
    
    # Purpose: Removes and returns the value associates with the given key
    def pop(self, key: str, default=None):
        return self.sessions.pop(key, default)
    
    # Purpose: Appends a message to the session's conversation history
    def add_to_history(self, message: str) -> None:
        if "history" not in self.sessions:
            self.sessions["history"] = []
        self.sessions["history"].append(message)

# region Strategy Pattern
# endregion

# QueryHandle: abstract class
class QueryHandler(ABC):
    # Purpose: Handles different query types and provides a common interface for all query handlers using the strategy pattern
    @abstractmethod
    def handle(self, query: str, backend_manager: BackendManager, session_manager: SessionManager) -> str:
        pass

class CharacterInfoHandler(QueryHandler):
    def handle(self, query: str, backend: BackendManager, session: SessionManager) -> str:
        char_name = self._extract_character(query)
        if char_name:
            return backend.process_request("character", char_name)
        return "Which character would you like information about?"

    def _extract_character(self, query: str) -> Optional[str]:
        characters = ['Gojo', 'Megumi', 'Nanami', 'Nobara', 'Sukuna']
        return next((c for c in characters if c.lower() in query.lower()), None)

class ActionInfoHandler(QueryHandler):
    def handle(self, query: str, backend: BackendManager, session: SessionManager) -> str:
        action = self._extract_action(query)
        if action:
            return backend.process_request("action", action)
        return "Which action would you like to know about? (Attack/Defend/Special)"

    def _extract_action(self, query: str) -> Optional[str]:
        actions = ['Attack', 'Defend', 'Special']
        return next((a for a in actions if a.lower() in query.lower()), None)

class GameAdviceHandler(QueryHandler):
    def handle(self, query: str, backend: BackendManager, session: SessionManager) -> str:
        return backend.process_request("advice")


# LiveAgentHandler: class
class LiveAgentHandler(QueryHandler):
    # Purpose: Handles requests to connect with a live agent depending on the query
    # Effect: Notifies agents about the customer request and returns the connection notification message to the user
    def handle(self, query: str, backend_manager: BackendManager, session_manager: SessionManager) -> str:
        LiveAgentNotifier.notify_agents(f"Customer requested live agent: {query}")
        return ResponseFactory.get_random_response("live_agent_connect")

# DefaultHandler: class
class DefaultHandler(QueryHandler):
    # Purpose: Handles for unrecognized queries and appends it into the txt file
    # Effect: Logs unrecognized queries and returns a generic response that input is not recognized to the user
    def handle(self, query: str, backend_manager: BackendManager, session_manager: SessionManager) -> str:
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            unrecognized_path = os.path.join(base_dir, 'unrecognized_queries.txt')
            with open(unrecognized_path, "a") as file:
                file.write(query + "\n")
        except:
            pass
        return ResponseFactory.get_random_response("default_response")

# region Observer Pattern
# endregion

# Observer: abstract class
class Observer(ABC):
    # Purpose: An interface for objects that should be notified of events using the observer pattern
    @abstractmethod
    def alert(self, message: str) -> None:
        pass

# LiveAgentObserver: class
class LiveAgentObserver(Observer):
    # Purpose: Live agent notifications with the message when an agent is alerted
    def alert(self, message: str) -> None:
        print(f"[LIVE AGENT NOTIFIED]: {message}")

# LiveAgentNotifier: class
class LiveAgentNotifier:
    # Purpose: Managaes observer notifications for live agent requests
    # Effect: Maintains a list of observers and notifies them when a customer requests a live agent
    _observers: List[Observer] = []
    
    # Purpose: Adds an observer (agent) to the list of observers
    @staticmethod
    def add_observer(observer: Observer) -> None:
        LiveAgentNotifier._observers.append(observer)
    
    # Purpose: Notifies all registers observers by calling their alert message
    @staticmethod
    def notify_agents(message: str) -> None:
        for observer in LiveAgentNotifier._observers:
            observer.alert(message)

# region Flyweight Pattern
# endregion 

# ResponseFactory: class
class ResponseFactory:
    # Purpose: Response templates and provides random selections to manage templates using the flyweight pattern
    _response_pools: Dict[str, List[str]] = {
        "default_response": [
            "I'm not sure about that. Let me check with our team and get back to you.",
            "I don't have that information at the moment. Please try asking something else.",
            "That's beyond my current knowledge. Let me make a note for our support team.",
            "I'll need to research that further. Can I help with something else in the meantime?"
        ],
        "negative_sentiment": [
            "I sincerely apologize for the inconvenience. Let me escalate this issue to a live agent now.",
            "I'm sorry to hear that. Let me connect you with a customer service representative who can help.",
            "I understand your frustration. I'm transferring you to a live agent who can resolve this immediately.",
            "I apologize for this situation. Let me connect you with someone who can help you right away."
        ]
    }
    
    # Purpose:  Provides a random response from the correct predefined category
    # Effect: If the category exists return a random response from the list of responses, otherwise, raise a value error
    @classmethod
    def get_random_response(cls, category: str) -> str:
        if category not in cls._response_pools:
            raise ValueError(f"Response category '{category}' not found")
        return random.choice(cls._response_pools[category])

# region Factory Pattern
# endregion

# Updated Query Manager
class QueryManager:
    def __init__(self) -> None:
        self.handlers = {
            "character_info": CharacterInfoHandler(),
            "action_info": ActionInfoHandler(),
            "game_advice": GameAdviceHandler()
        }

    def get_handler(self, intent: str) -> QueryHandler:
        return self.handlers.get(intent, DefaultHandler())

class IntentRecognitionService:
    def __init__(self):
        self._intent_phrases = {
            "character_info": [
                "tell me about", "character info", "what does", "do?",
                "abilities", "special move", "stats"
            ],
            "action_info": [
                "how does work", "what is", "action",
                "attack do", "defend do", "special do"
            ],
            "game_advice": [
                "tips", "advice", "strategy", "should I",
                "recommend", "best way", "how to win"
            ]
        }

    def recognize_intent(self, query: str) -> str:
        query_lower = query.lower()
        for intent, phrases in self._intent_phrases.items():
            if any(phrase in query_lower for phrase in phrases):
                return intent
        return "unknown"

# SentimentAnalyzer: class
class SentimentAnalyzer:
    # Purpose: Has a list of negative and strong negative words that detects when the user is upset
    # Effect: The live agent is then notified to directly bring the user to be attended by a professional
    def __init__(self):
        self.negative_words: List[str] = [
            "angry", "frustrated", "ridiculous", "terrible", "awful", "disappointed", 
            "delay", "delayed", "wait", "waited", "slow", "bad", "worst", "hate",
            "unacceptable", "poor", "useless", "complaint", "annoyed", "annoying"
        ]

        self.strong_negative_phrases: List[str] = [
            "this is ridiculous", "worst service", "terrible experience", 
            "never shopping again", "waste of money", "absolutely useless"
        ]
    
    # Purpose: Analyzes user input for any negative input or escalation to alert the live agents when needed
    def detect_negative_sentiment(self, user_input: str) -> bool:
        user_input_lower: str = user_input.lower()

        if any(phrase in user_input_lower for phrase in self.strong_negative_phrases):
            return True

        return any(word in user_input_lower for word in self.negative_words)

# region Facade Pattern
# endregion

# Chatbot: class
class Chatbot:
    # Purpose: Simple interface to control all components to process user queries and generate appropriate responses using the facade pattern
    def __init__(self) -> None:
        self.backend_manager = BackendManager()
        self.query_manager = QueryManager()
        self.session_manager = SessionManager()
        self.intent_service = IntentRecognitionService()
        self.sentiment_analyzer = SentimentAnalyzer()
        
        LiveAgentNotifier.add_observer(LiveAgentObserver())

    # Purpose: Resets the session by clearing up all the session data
    def reset_session(self):
        self.session_manager.sessions = {}

    # Purpose: Gets the conversation history from the session manager
    def get_conversation_history(self):
        return self.session_manager.get("history", [])

    # Purpose: Determines the appropriate intent and returns a response
    # Effect: Session management, sentinment analysis, database lookups, and intent recognition to ensure query handling 
    def process_query(self, query):
        self.session_manager.add_to_history(query)
        
        # Handle awaiting order ID with refund
        if self.session_manager.get("awaiting_order_id") and self.session_manager.get("refund"):
            handler = self.query_manager.get_handler("refund")
            return handler.handle(query, self.backend_manager, self.session_manager)
        
        # Handle awaiting order ID without refund
        if self.session_manager.get("awaiting_order_id"):
            handler = self.query_manager.get_handler("order")
            return handler.handle(query, self.backend_manager, self.session_manager)
        
        # Handle awaiting refund reason
        if self.session_manager.get("awaiting_refund_reason"):
            handler = self.query_manager.get_handler("refund_reason")
            return handler.handle(query, self.backend_manager, self.session_manager)
        
        # Handle negative sentiment
        if self.sentiment_analyzer.detect_negative_sentiment(query):
            LiveAgentNotifier.notify_agents(f"Customer with negative sentiment: {query}")
            return ResponseFactory.get_random_response("negative_sentiment")
        
        # Determine intent and handle query
        intent = self.intent_service.recognize_intent(query)
        handler = self.query_manager.get_handler(intent)
        return handler.handle(query, self.backend_manager, self.session_manager)

# region Client Code
# endregion    

# Client code
if __name__ == "__main__":
    chatbot = Chatbot()
    print("Welcome to the PirateEase Chatbot!")
    print("Type 'bye' to exit or 'help' for assistance.")
    
    while True:
        user_input = input("\nUser: ")
        if user_input.lower() == "bye":
            print("Chatbot: Goodbye!")
            break
        elif user_input.lower() == "help":
            print("Chatbot: You can ask me about your order status, refund requests, product availability, or connect you to a live agent.")
            continue
            
        response = chatbot.process_query(user_input)
        print("Chatbot:", response)