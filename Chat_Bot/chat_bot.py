import json
import os
import random
import re
from abc import ABC, abstractmethod
from typing import *

# OrderService: class
class OrderService:
    # Purpose: Backend service that prints out the return responses from ChatBot about a delivery
    def track_order(self, order_id: str) -> str:
        delivery_status: List[str] = ["out for delivery and will arrive today by 5 PM",
                                     "in transit and will arrive tomorrow",
                                     "at the local distribution center and will arrive within 2 days"]
        return f"Your order is {random.choice(delivery_status)}."

# RefundService: class
class RefundService:
    # Purpose: Backend service that prints out the return response from ChatBot about a refund
    def process_refund(self, order_id: str, reason: Optional[str] = None) -> str:
        if reason:
            return f"Your refund request for a {reason} product has been submitted. Expect the refund in 5-7 business days."
        else:
            return "Your refund request has been submitted. Expect the refund in 5-7 business days."

# ProductService: class
class ProductService:
    # Purpose: Manages product inventory and provides methods to check and extract product information
    def __init__(self):
        self.products: List[str] = ["iPhone 15 Pro", "iPhone 15", "iPhone",
                                    "MacBook Air", "MacBook", "Mac Pro", 
                                     "iPad Pro", "iPad", "AirPods", "Smartphone"]
    
    # Purpose: Has the stored products in inventory and checks if the given user is searching for one of the items in stock
    # Effect: If the item is in stock return that the product is available, otherwise, return that the product is out of stock
    def check_availability(self, product_name: str) -> str:
        if product_name.lower() in [p.lower() for p in self.products]:
            return f"Checking inventory... the {product_name} is currently available."
        else:
            return f"Checking inventory... sorry, it is currently out of stock. We expect new inventory next week."
    
    # Purpose: Gets the list of products from the class itself in self.products being initialized
    def get_product_list(self) -> List[str]:
        return self.products
        
    # Purpose: Extracts the products name if in the given list of products in inventory, handling lowercase and common words that may interfere
    # Effect: If the product is in the query, return the product, otherwise just return an empty string
    def extract_product_name(self, query: str) -> Optional[str]:
        query_lower = query.lower()
        for product in self.products:
            if product.lower() in query_lower:
                return product
        common_words = ["is", "the", "available", "in", "stock", "do", "you", "have", 
                      "check", "inventory", "checking", "availability", "of", "for"]        
        words = query_lower.split()
        candidate_words = [word for word in words if word not in common_words]
        if candidate_words:
            return candidate_words[0].capitalize()
        return ""

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
    # Purpose: Uses the adapter pattern to provide an interface to the multiple backend services
    def __init__(self) -> None:
        self.order_service = OrderService()
        self.refund_service = RefundService()
        self.product_service = ProductService()
        self.live_agent_service = LiveAgentService()

    # Purpose: Retrieves to the appropriate service based on the request type and return the appropriate response
    def process_request(self, request_type: str, *args: Any) -> str:
        if request_type == "order":
            return self.order_service.track_order(args[0])
        elif request_type == "refund":
            return self.refund_service.process_refund(args[0], args[1] if len(args) > 1 else None)
        elif request_type == "product":
            return self.product_service.check_availability(args[0])
        elif request_type == "live_agent":
            return self.live_agent_service.connect()
        return "Service not available."
    
    # Purpose: Provides direct access to the produce service objects and items in storage for usage
    def get_product_service(self) -> ProductService:
        return self.product_service

# QueryDatabase: class
class QueryDatabase:
    # Purpose: Loads and stores the predefined queries and their responses from a JSON file
    # Effect: Provides a mechanism to match user queries with the predefined responses
    def __init__(self, filepath: Optional[str] = None) -> None:
        if filepath is None:
            base_dir: str = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(base_dir, "queries.json")
        if not os.path.exists(filepath):
            self.queries = {}
        else:
            with open(filepath, "r") as file:
                self.queries = json.load(file)

    # Purpose: Cleans the input by removing extra punctuation and spaces and see if it matches with one of the questions in the query
    # Effect: If the response exists in the query, return the expected response, otherwise return an empty string
    def get_response(self, user_input: str) -> Optional[str]:
        clean_input = re.sub(r'[^\w\s]', '', user_input).lower().strip()
        if clean_input in self.queries:
            return self.queries[clean_input]
        for query, response in self.queries.items():
            clean_query = re.sub(r'[^\w\s]', '', query).lower().strip()
            if clean_input == clean_query:
                return response
        return ""

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

# OrderTrackingHandler: class
class OrderTrackingHandler(QueryHandler):
    # Purpose: Handles order tracking requests from the user, requesting order ID if needed
    # Effect: If the order ID has already been entered, do not ask for it again and to use the one in storage
    def handle(self, query: str, backend_manager: BackendManager, session_manager: SessionManager) -> str:
        if session_manager.get("order_id"):
            order_id = session_manager.get("order_id")
            return backend_manager.process_request("order", order_id)
        
        if session_manager.get("awaiting_order_id"):
            session_manager.set("order_id", query)
            session_manager.set("awaiting_order_id", False)
            return backend_manager.process_request("order", query)
        
        session_manager.set("awaiting_order_id", True)
        return ResponseFactory.get_random_response("order_id_request")

# RefundHandler: class
class RefundHandler(QueryHandler):
    # Purpose: Handles the refund requests from the user, requesting order ID if needed
    # Effect: If the order ID has already been entered, do not ask for it again and to use the one in storage
    def handle(self, query: str, backend_manager: BackendManager, session_manager: SessionManager) -> str:
        if session_manager.get("order_id"):
            order_id = session_manager.get("order_id")
            session_manager.set("awaiting_refund_reason", True)
            return ResponseFactory.get_random_response("refund_reason_request")
        
        if session_manager.get("awaiting_order_id"):
            session_manager.set("awaiting_order_id", False)
            session_manager.set("order_id", query)
            session_manager.set("awaiting_refund_reason", True)
            return ResponseFactory.get_random_response("refund_reason_request")
            
        session_manager.set("awaiting_order_id", True)
        return ResponseFactory.get_random_response("order_id_request")

# RefundReasonHandler: class
class RefundReasonHandler(QueryHandler):
    # Purpose: Process the refund reason after an order ID is provided
    # Effect: Completes the refund process with the provided reason once the order ID is inputted or in storage
    def handle(self, query: str, backend_manager: BackendManager, session_manager: SessionManager) -> str:
        if session_manager.get("awaiting_refund_reason"):
            order_id = session_manager.get("order_id", "")
            refund_reason = query.lower()
            
            session_manager.pop("awaiting_refund_reason", None)
            session_manager.pop("awaiting_order_id", None)
            session_manager.pop("refund", None)
            
            return backend_manager.process_request("refund", order_id, refund_reason)
        return ResponseFactory.get_random_response("order_id_request")

# ProductAvailabilityHandler: class
class ProductAvailabilityHandler(QueryHandler):
    # Purpose: Handles which products are available in the queries and in storage
    # Effect: Extracts the product name from the query and checks if it is available
    def handle(self, query: str, backend_manager: BackendManager, session_manager: SessionManager) -> str:
        product_service = backend_manager.get_product_service()
        product_name = product_service.extract_product_name(query)
        if not product_name:
            return ResponseFactory.get_random_response("product_request")
        return backend_manager.process_request("product", product_name)

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
        "order_id_request": [
            "Please enter your order ID.",
            "I'll need your order ID to check that for you.",
            "Could you provide your order ID so I can look that up?",
            "What's your order ID? I'll track that for you right away."
        ],
        "refund_reason_request": [
            "Why are you returning the product? (e.g., defective, wrong item, changed mind)",
            "Could you tell me the reason for your return?",
            "What seems to be the issue with your product?",
            "Please specify why you're requesting a refund."
        ],
        "product_request": [
            "Please specify which product you're looking for.",
            "Which product would you like to check availability for?",
            "I'd be happy to check stock for you. Which item are you interested in?",
            "Could you tell me the name of the product you're asking about?"
        ],
        "live_agent_connect": [
            "Connecting you to a live agent now...",
            "I'll transfer you to a customer service representative right away.",
            "Let me connect you with one of our specialists.",
            "I'm bringing in a professional agent now to help you with this."
        ],
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

# QueryManager: class
class QueryManager:
    # Purpose: Create appropriate query handles and handles instances by returning the correct handler using the factory pattern
    def __init__(self) -> None:
        self.handlers: Dict[str, QueryHandler] = {
            "order": OrderTrackingHandler(),
            "refund": RefundHandler(),
            "refund_reason": RefundReasonHandler(),
            "product": ProductAvailabilityHandler(),
            "live_agent": LiveAgentHandler()
        }

    # Purpose: Provides the correct instance of a handler based on the query type
    # Effect: If it exists return the corresponding query handler, otherwise, return the default handler
    def get_handler(self, query_type: str) -> QueryHandler:
        return self.handlers.get(query_type, DefaultHandler())

# IntentRecognitionService: class
class IntentRecognitionService:
    # Purpose: Analyze the user's input to determine their intent
    # Effect: Categorizes queries into the predefined intent types based on synonym matching
    def __init__(self):
        self._intent_phrases: Dict[str, List[str]] = {
            "order": [
                "where is my order", "track my package", "track my order", "order status",
                "delivery status", "shipping status", "where's my order", "when will my order arrive", 
                "check my order", "find my order", "locate my order", "where is my delivery", 
                "what's the status of my order", "has my order been delivered", "package tracking",
                "delivery tracking", "shipment location", "order whereabouts", "delivery timeline",
                "track shipment", "delivery information", "shipping update", "when will it arrive",
                "expected delivery", "delivery time", "package location", "is my order on the way"
            ],
            "refund": [
                "return my product", "refund", "return", "refund request", "i want to return", "i want a refund", 
                "send back my order", "cancel my order", "i don't want my order anymore", 
                "return policy", "how do i return", "product return", "money back", "return process",
                "refund eligibility", "return authorization", "return procedure", "cancel purchase",
                "wrong item", "defective product", "damaged product", "not satisfied", "money refund",
                "exchange item", "replacement", "return label", "return merchandise", "cancel transaction"
            ],
            "product": [
                "is the product available", "availability", "stock status", "do you have", 
                "in stock", "check inventory", "is there stock for", "can i buy", 
                "is the item available", "when will you restock", "product in stock",
                "inventory check", "still selling", "available for purchase", "available to buy",
                "can I order", "do you sell", "looking for", "searching for", "when will you have",
                "product availability", "back in stock", "out of stock", "current inventory",
                "stock levels", "product supply", "available units", "stock quantity"
            ],
            "live_agent": [
                "talk to a human", "customer support", "need help", "help with my order", 
                "speak to a representative", "customer service", "agent", "human support", 
                "connect me with", "talk to someone", "real person", "live support",
                "representative", "supervisor", "customer care", "human assistance",
                "speak to a person", "real agent", "connect to staff", "need a human",
                "talk to a person", "live chat", "customer agent", "help desk", "service desk",
                "speak with agent", "customer rep", "talk to manager", "service representative"
            ]
        }

    # Purpose: Analyzes the user's input to determine the most appropriate intent category
    # Effect: Cleans the user's input and searches the known intent phrases to then handle the special cases
    def recognize_intent(self, user_input: str, product_list: List[str], queries: Dict) -> str:
        clean_input = re.sub(r'[^\w\s]', '', user_input.lower()).strip()
        
        if clean_input in queries:
            if "order" in clean_input or "track" in clean_input or "delivery" in clean_input:
                return "order"
            if "refund" in clean_input or "return" in clean_input:
                return "refund"
            if "product" in clean_input or "stock" in clean_input:
                return "product"
            if "agent" in clean_input or "human" in clean_input:
                return "live_agent"
            
        for intent, phrases in self._intent_phrases.items():
            for phrase in phrases:
                if phrase in clean_input:
                    return intent
                
        if any(product.lower() in clean_input for product in product_list):
            return "product"       
        if any(term in clean_input for term in ["stock", "available", "inventory"]):
            return "product"
        if "track" in clean_input and ("package" in clean_input or "order" in clean_input):
            return "order"
        
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
        self.query_db = QueryDatabase()
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
        
        # Check for response in database
        db_response = self.query_db.get_response(query)
        if db_response:
            return db_response
        
        # Determine intent and handle query
        product_list = self.backend_manager.get_product_service().get_product_list()
        intent = self.intent_service.recognize_intent(query, product_list, self.query_db.queries)
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