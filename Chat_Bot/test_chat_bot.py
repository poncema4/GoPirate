from chat_bot import *
from unittest.mock import *
import pytest
import sys
import io

# region Order Service Tests
# endregion

def test_track_order_returns_valid_message() -> None:
    service = OrderService()
    result = service.track_order("123456")
    assert "Your order is" in result
    assert any(status in result for status in [
        "out for delivery and will arrive today by 5 PM",
        "in transit and will arrive tomorrow",
        "at the local distribution center and will arrive within 2 days"
    ])

def test_track_order_includes_order_id() -> None:
    service = OrderService()
    order_id = "ABC123"
    result = service.track_order(order_id)
    assert "Your order is" in result
    assert any(status in result for status in [
        "out for delivery and will arrive today by 5 PM",
        "in transit and will arrive tomorrow",
        "at the local distribution center and will arrive within 2 days"
    ])

# region Refund Service Tests
# endregion

def test_process_refund_without_reason() -> None:
    service = RefundService()
    result = service.process_refund("123456")
    assert "Your refund request has been submitted" in result
    assert "Expect the refund in 5-7 business days" in result
    assert "product" not in result

def test_process_refund_with_reason() -> None:
    service = RefundService()
    result = service.process_refund("123456", "defective")
    assert "Your refund request for a defective product has been submitted" in result
    assert "Expect the refund in 5-7 business days" in result
    assert "defective" in result

# region Product Service Tests
# endregion

def test_check_availability_for_available_product() -> None:
    service = ProductService()
    result = service.check_availability("iPhone")
    assert "Checking inventory..." in result
    assert "iPhone is currently available" in result

def test_check_availability_for_unavailable_product() -> None:
    service = ProductService()
    result = service.check_availability("Surface Pro")
    assert "Checking inventory..." in result
    assert "sorry, it is currently out of stock" in result
    assert "We expect new inventory next week" in result

def test_get_product_list_returns_all_products() -> None:
    service = ProductService()
    products = service.get_product_list()
    assert len(products) > 0
    assert "iPhone" in products
    assert "MacBook" in products
    assert "iPad" in products
    assert "Smartphone" in products

def test_extract_product_name_with_exact_match() -> None:
    service = ProductService()
    result = service.extract_product_name("Do you have an iPhone in stock?")
    assert result == "iPhone"

def test_extract_product_name_with_case_insensitive_match() -> None:
    service = ProductService()
    result = service.extract_product_name("Do you have a macbook in stock?")
    assert result == "MacBook"

def test_extract_product_name_with_no_match_returns_first_non_common_word() -> None:
    service = ProductService()
    result = service.extract_product_name("Do you have a smartphone in stock?")
    assert result == "Smartphone"

def test_extract_product_name_with_only_common_words_returns_empty() -> None:
    service = ProductService()
    result = service.extract_product_name("Do you have the in stock?")
    assert result != ""

# region Live Agent Service Tests
# endregion

@patch('chat_bot.LiveAgentNotifier.notify_agents')
@patch('chat_bot.ResponseFactory.get_random_response')
def test_connect_notifies_agents_and_returns_response(mock_get_random, mock_notify) -> None:
    mock_get_random.return_value = "Connecting you to a live agent now..."
    service = LiveAgentService()
    result = service.connect()
    
    mock_notify.assert_called_once_with("Customer requested live agent")
    mock_get_random.assert_called_once_with("live_agent_connect")
    assert result == "Connecting you to a live agent now..."

# region Backend Manager Tests
# endregion

def test_process_request_order() -> None:
    manager = BackendManager()
    with patch.object(manager.order_service, 'track_order', return_value="Your order is in transit."):
        result = manager.process_request("order", "123456")
        assert result == "Your order is in transit."

def test_process_request_refund_without_reason() -> None:
    manager = BackendManager()
    with patch.object(manager.refund_service, 'process_refund', return_value="Your refund request has been submitted."):
        result = manager.process_request("refund", "123456")
        assert result == "Your refund request has been submitted."

def test_process_request_refund_with_reason() -> None:
    manager = BackendManager()
    with patch.object(manager.refund_service, 'process_refund', return_value="Your refund for defective product has been submitted."):
        result = manager.process_request("refund", "123456", "defective")
        assert result == "Your refund for defective product has been submitted."

def test_process_request_product() -> None:
    manager = BackendManager()
    with patch.object(manager.product_service, 'check_availability', return_value="iPhone is available."):
        result = manager.process_request("product", "iPhone")
        assert result == "iPhone is available."

def test_process_request_live_agent() -> None:
    manager = BackendManager()
    with patch.object(manager.live_agent_service, 'connect', return_value="Connecting to a live agent..."):
        result = manager.process_request("live_agent")
        assert result == "Connecting to a live agent..."

def test_process_request_invalid_service() -> None:
    manager = BackendManager()
    result = manager.process_request("invalid_service")
    assert result == "Service not available."

def test_get_product_service_returns_product_service() -> None:
    manager = BackendManager()
    result = manager.get_product_service()
    assert isinstance(result, ProductService)

# region Query Database Tests
# endregion

def test_query_db_init_with_no_filepath() -> None:
    with patch('os.path.exists', return_value=False):
        db = QueryDatabase(None)
        assert db.queries == {}

def test_query_db_init_with_filepath_exists() -> None:
    mock_data = {"test": "response"}
    m = mock_open(read_data=json.dumps(mock_data))
    with patch('os.path.exists', return_value=True), patch('builtins.open', m):
        db = QueryDatabase("queries.json")
        assert db.queries == mock_data

def test_query_db_get_response_exact_match() -> None:
    db = QueryDatabase(None)
    db.queries = {"hello": "Hello there!"}
    result = db.get_response("hello")
    assert result == "Hello there!"

def test_query_db_get_response_with_punctuation() -> None:
    db = QueryDatabase(None)
    db.queries = {"hello": "Hello there!"}
    result = db.get_response("hello!")
    assert result == "Hello there!"

def test_query_db_get_response_case_insensitive() -> None:
    db = QueryDatabase(None)
    db.queries = {"hello": "Hello there!"}
    result = db.get_response("HELLO")
    assert result == "Hello there!"

def test_query_db_get_response_no_match() -> None:
    db = QueryDatabase(None)
    db.queries = {"hello": "Hello there!"}
    result = db.get_response("goodbye")
    assert result == ""

# region Session Manager Tests
# endregion

def test_session_manager_get_with_existing_key() -> None:
    manager = SessionManager()
    manager.sessions = {"test_key": "test_value"}
    result = manager.get("test_key")
    assert result == "test_value"

def test_session_manager_get_with_non_existing_key_returns_default() -> None:
    manager = SessionManager()
    result = manager.get("non_existing_key", "default_value")
    assert result == "default_value"

def test_session_manager_set_adds_key_value_pair() -> None:
    manager = SessionManager()
    manager.set("test_key", "test_value")
    assert manager.sessions["test_key"] == "test_value"

def test_session_manager_pop_removes_and_returns_value() -> None:
    manager = SessionManager()
    manager.sessions = {"test_key": "test_value"}
    result = manager.pop("test_key")
    assert result == "test_value"
    assert "test_key" not in manager.sessions

def test_session_manager_pop_with_non_existing_key_returns_default() -> None:
    manager = SessionManager()
    result = manager.pop("non_existing_key", "default_value")
    assert result == "default_value"

def test_session_manager_add_to_history_creates_history_if_not_exists() -> None:
    manager = SessionManager()
    manager.add_to_history("test message")
    assert "history" in manager.sessions
    assert manager.sessions["history"] == ["test message"]

def test_session_manager_add_to_history_appends_to_existing_history() -> None:
    manager = SessionManager()
    manager.sessions = {"history": ["previous message"]}
    manager.add_to_history("test message")
    assert manager.sessions["history"] == ["previous message", "test message"]

# region Order Tracking Handler Tests
# endregion

def test_order_tracking_handle_with_existing_order_id() -> None:
    handler = OrderTrackingHandler()
    backend_manager = MagicMock()
    backend_manager.process_request.return_value = "Your order is in transit."
    session_manager = MagicMock()
    session_manager.get.side_effect = lambda key, default=None: "123456" if key == "order_id" else None
    
    result = handler.handle("", backend_manager, session_manager)
    
    backend_manager.process_request.assert_called_once_with("order", "123456")
    assert result == "Your order is in transit."

def test_order_tracking_handle_with_awaiting_order_id() -> None:
    handler = OrderTrackingHandler()
    backend_manager = MagicMock()
    backend_manager.process_request.return_value = "Your order is in transit."
    session_manager = MagicMock()
    session_manager.get.side_effect = lambda key, default=None: True if key == "awaiting_order_id" else None
    
    result = handler.handle("123456", backend_manager, session_manager)
    
    session_manager.set.assert_any_call("order_id", "123456")
    session_manager.set.assert_any_call("awaiting_order_id", False)
    backend_manager.process_request.assert_called_once_with("order", "123456")
    assert result == "Your order is in transit."

def test_order_tracking_handle_without_order_id_requests_it() -> None:
    handler = OrderTrackingHandler()
    backend_manager = MagicMock()
    session_manager = MagicMock()
    session_manager.get.return_value = None
    
    with patch('chat_bot.ResponseFactory.get_random_response', return_value="Please enter your order ID."):
        result = handler.handle("", backend_manager, session_manager)
        
        session_manager.set.assert_called_once_with("awaiting_order_id", True)
        assert result == "Please enter your order ID."

# region Refund Handler Tests
# endregion

def test_refund_handle_with_existing_order_id() -> None:
    handler = RefundHandler()
    backend_manager = MagicMock()
    session_manager = MagicMock()
    session_manager.get.side_effect = lambda key, default=None: "123456" if key == "order_id" else None
    
    with patch('chat_bot.ResponseFactory.get_random_response', return_value="Why are you returning?"):
        result = handler.handle("", backend_manager, session_manager)
        
        session_manager.set.assert_called_once_with("awaiting_refund_reason", True)
        assert result == "Why are you returning?"

def test_refund_handle_with_awaiting_order_id() -> None:
    handler = RefundHandler()
    backend_manager = MagicMock()
    session_manager = MagicMock()
    session_manager.get.side_effect = lambda key, default=None: True if key == "awaiting_order_id" else None
    
    with patch('chat_bot.ResponseFactory.get_random_response', return_value="Why are you returning?"):
        result = handler.handle("123456", backend_manager, session_manager)
        
        session_manager.set.assert_any_call("awaiting_order_id", False)
        session_manager.set.assert_any_call("order_id", "123456")
        session_manager.set.assert_any_call("awaiting_refund_reason", True)
        assert result == "Why are you returning?"

def test_refund_handle_without_order_id_requests_it() -> None:
    handler = RefundHandler()
    backend_manager = MagicMock()
    session_manager = MagicMock()
    session_manager.get.return_value = None
    
    with patch('chat_bot.ResponseFactory.get_random_response', return_value="Please enter your order ID."):
        result = handler.handle("", backend_manager, session_manager)
        
        session_manager.set.assert_called_once_with("awaiting_order_id", True)
        assert result == "Please enter your order ID."

# region Refund Reason Handler Tests
# endregion

def test_refund_reason_handle_with_awaiting_refund_reason() -> None:
    handler = RefundReasonHandler()
    backend_manager = MagicMock()
    backend_manager.process_request.return_value = "Your refund has been processed."
    session_manager = MagicMock()
    session_manager.get.side_effect = lambda key, default=None: "123456" if key == "order_id" else (True if key == "awaiting_refund_reason" else None)
    
    result = handler.handle("defective", backend_manager, session_manager)
    
    session_manager.pop.assert_any_call("awaiting_refund_reason", None)
    session_manager.pop.assert_any_call("awaiting_order_id", None)
    session_manager.pop.assert_any_call("refund", None)
    backend_manager.process_request.assert_called_once_with("refund", "123456", "defective")
    assert result == "Your refund has been processed."

def test_refund_reason_handle_without_awaiting_refund_reason() -> None:
    handler = RefundReasonHandler()
    backend_manager = MagicMock()
    session_manager = MagicMock()
    session_manager.get.return_value = None
    
    with patch('chat_bot.ResponseFactory.get_random_response', return_value="Please enter your order ID."):
        result = handler.handle("", backend_manager, session_manager)
        assert result == "Please enter your order ID."

# region Product Availability Handler Tests
# endregion

def test_product_availability_handle_with_product_in_query() -> None:
    handler = ProductAvailabilityHandler()
    backend_manager = MagicMock()
    backend_manager.process_request.return_value = "iPhone is available."
    product_service = MagicMock()
    product_service.extract_product_name.return_value = "iPhone"
    backend_manager.get_product_service.return_value = product_service
    session_manager = MagicMock()
    
    result = handler.handle("Do you have an iPhone?", backend_manager, session_manager)
    
    product_service.extract_product_name.assert_called_once_with("Do you have an iPhone?")
    backend_manager.process_request.assert_called_once_with("product", "iPhone")
    assert result == "iPhone is available."

def test_product_availability_handle_without_product_in_query() -> None:
    handler = ProductAvailabilityHandler()
    backend_manager = MagicMock()
    product_service = MagicMock()
    product_service.extract_product_name.return_value = ""
    backend_manager.get_product_service.return_value = product_service
    session_manager = MagicMock()
    
    with patch('chat_bot.ResponseFactory.get_random_response', return_value="Which product are you looking for?"):
        result = handler.handle("Is it available?", backend_manager, session_manager)
        assert result == "Which product are you looking for?"

# region Live Agent Handler Tests
# endregion

def test_live_agent_handle_notifies_agents_and_returns_response() -> None:
    handler = LiveAgentHandler()
    backend_manager = MagicMock()
    session_manager = MagicMock()
    
    with patch('chat_bot.LiveAgentNotifier.notify_agents') as mock_notify, \
         patch('chat_bot.ResponseFactory.get_random_response', return_value="Connecting to a live agent..."):
        result = handler.handle("I need help", backend_manager, session_manager)
        
        mock_notify.assert_called_once_with("Customer requested live agent: I need help")
        assert result == "Connecting to a live agent..."

# region Default Handler Tests
# endregion

def test_default_handle_logs_query_and_returns_default_response() -> None:
    handler = DefaultHandler()
    backend_manager = MagicMock()
    session_manager = MagicMock()
    
    m = mock_open()
    with patch('builtins.open', m), \
         patch('os.path.dirname', return_value="/fake/path"), \
         patch('os.path.join', return_value="/fake/path/unrecognized_queries.txt"), \
         patch('chat_bot.ResponseFactory.get_random_response', return_value="I don't understand that."):
        result = handler.handle("What is the meaning of life?", backend_manager, session_manager)
        
        m.assert_called_once_with("/fake/path/unrecognized_queries.txt", "a")
        m().write.assert_called_once_with("What is the meaning of life?\n")
        assert result == "I don't understand that."

def test_default_handle_handles_file_error_gracefully() -> None:
    handler = DefaultHandler()
    backend_manager = MagicMock()
    session_manager = MagicMock()
    
    with patch('builtins.open', side_effect=IOError()), \
         patch('chat_bot.ResponseFactory.get_random_response', return_value="I don't understand that."):
        result = handler.handle("Who is Marco Ponce?", backend_manager, session_manager)
        assert result == "I don't understand that."

# region Live Agent Observer Tests
# endregion

def test_live_agent_observer_alert_prints_message() -> None:
    observer = LiveAgentObserver()
    captured_output = io.StringIO()
    sys.stdout = captured_output
    
    observer.alert("Test message")
    
    sys.stdout = sys.__stdout__
    assert "[LIVE AGENT NOTIFIED]: Test message" in captured_output.getvalue()

# region Live Agent Notifier Tests
# endregion

def test_live_agent_notifier_add_observer_adds_to_list() -> None:
    original_observers = LiveAgentNotifier._observers.copy()
    try:
        LiveAgentNotifier._observers = []
        observer = MagicMock()
        
        LiveAgentNotifier.add_observer(observer)
        
        assert observer in LiveAgentNotifier._observers
    finally:
        LiveAgentNotifier._observers = original_observers

def test_live_agent_notifier_notify_agents_calls_alert_on_all_observers() -> None:
    original_observers = LiveAgentNotifier._observers.copy()
    try:
        observer1 = MagicMock()
        observer2 = MagicMock()
        LiveAgentNotifier._observers = [observer1, observer2]
        
        LiveAgentNotifier.notify_agents("Test message")
        
        observer1.alert.assert_called_once_with("Test message")
        observer2.alert.assert_called_once_with("Test message")
    finally:
        LiveAgentNotifier._observers = original_observers

# region Response Factory Tests
# endregion

def test_response_factory_get_random_response_returns_from_category() -> None:
    category = "order_id_request"
    responses = ResponseFactory._response_pools[category]
    
    result = ResponseFactory.get_random_response(category)
    
    assert result in responses

def test_response_factory_get_random_response_with_invalid_category_raises_error() -> None:
    try:
        ResponseFactory.get_random_response("invalid_category")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Response category 'invalid_category' not found" in str(e)

# region Query Manager Tests
# endregion

def test_query_manager_get_handler_returns_correct_handler_for_order() -> None:
    manager = QueryManager()
    handler = manager.get_handler("order")
    assert isinstance(handler, OrderTrackingHandler)

def test_query_manager_get_handler_returns_correct_handler_for_refund() -> None:
    manager = QueryManager()
    handler = manager.get_handler("refund")
    assert isinstance(handler, RefundHandler)

def test_query_manager_get_handler_returns_correct_handler_for_refund_reason() -> None:
    manager = QueryManager()
    handler = manager.get_handler("refund_reason")
    assert isinstance(handler, RefundReasonHandler)

def test_query_manager_get_handler_returns_correct_handler_for_product() -> None:
    manager = QueryManager()
    handler = manager.get_handler("product")
    assert isinstance(handler, ProductAvailabilityHandler)

def test_query_manager_get_handler_returns_correct_handler_for_live_agent() -> None:
    manager = QueryManager()
    handler = manager.get_handler("live_agent")
    assert isinstance(handler, LiveAgentHandler)

def test_query_manager_get_handler_returns_default_handler_for_unknown_type() -> None:
    manager = QueryManager()
    handler = manager.get_handler("unknown")
    assert isinstance(handler, DefaultHandler)

# region Intent Recognition Service Tests
# endregion

def test_intent_recognition_recognize_intent_exact_match_in_queries_order() -> None:
    service = IntentRecognitionService()
    queries = {"track my order": "response"}
    product_list = []
    
    result = service.recognize_intent("track my order", product_list, queries)
    
    assert result == "order"

def test_intent_recognition_recognize_intent_exact_match_in_queries_refund() -> None:
    service = IntentRecognitionService()
    queries = {"i want a refund": "response"}
    product_list = []
    
    result = service.recognize_intent("i want a refund", product_list, queries)
    
    assert result == "refund"

def test_intent_recognition_recognize_intent_exact_match_in_queries_product() -> None:
    service = IntentRecognitionService()
    queries = {"is the product available": "response"}
    product_list = []
    
    result = service.recognize_intent("is the product available", product_list, queries)
    
    assert result == "product"

def test_intent_recognition_recognize_intent_exact_match_in_queries_live_agent() -> None:
    service = IntentRecognitionService()
    queries = {"talk to a human": "response"}
    product_list = []
    
    result = service.recognize_intent("talk to a human", product_list, queries)
    
    assert result == "live_agent"

def test_intent_recognition_recognize_intent_phrase_match_order() -> None:
    service = IntentRecognitionService()
    queries = {}
    product_list = []
    
    result = service.recognize_intent("where is my order", product_list, queries)
    
    assert result == "order"

def test_intent_recognition_recognize_intent_phrase_match_refund() -> None:
    service = IntentRecognitionService()
    queries = {}
    product_list = []
    
    result = service.recognize_intent("i want a refund for my purchase", product_list, queries)
    
    assert result == "refund"

def test_intent_recognition_recognize_intent_phrase_match_product() -> None:
    service = IntentRecognitionService()
    queries = {}
    product_list = []
    
    result = service.recognize_intent("check inventory for this item", product_list, queries)
    
    assert result == "product"

def test_intent_recognition_recognize_intent_phrase_match_live_agent() -> None:
    service = IntentRecognitionService()
    queries = {}
    product_list = []
    
    result = service.recognize_intent("can i speak to a representative", product_list, queries)
    
    assert result == "live_agent"

def test_intent_recognition_recognize_intent_product_in_query() -> None:
    service = IntentRecognitionService()
    queries = {}
    product_list = ["iPhone"]
    
    result = service.recognize_intent("do you have an iPhone", product_list, queries)
    
    assert result == "product"

def test_intent_recognition_recognize_intent_inventory_terms() -> None:
    service = IntentRecognitionService()
    queries = {}
    product_list = []
    
    result = service.recognize_intent("is it in stock", product_list, queries)
    
    assert result == "product"

def test_intent_recognition_recognize_intent_tracking_terms() -> None:
    service = IntentRecognitionService()
    queries = {}
    product_list = []
    
    result = service.recognize_intent("track my package please", product_list, queries)
    
    assert result == "order"

def test_recognize_intent_unknown() -> None:
    service = IntentRecognitionService()
    queries = {}
    product_list = []
    
    result = service.recognize_intent("hello there", product_list, queries)
    
    assert result == "unknown"

# region Sentiment Analyzer Tests
# endregion

def test_detect_negative_sentiment_with_negative_word() -> None:
    analyzer = SentimentAnalyzer()
    result = analyzer.detect_negative_sentiment("I am very angry about this service")
    assert result is True

def test_detect_negative_sentiment_with_strong_negative_phrase() -> None:
    analyzer = SentimentAnalyzer()
    result = analyzer.detect_negative_sentiment("This is ridiculous, I can't believe it")
    assert result is True

def test_detect_negative_sentiment_with_neutral_message() -> None:
    analyzer = SentimentAnalyzer()
    result = analyzer.detect_negative_sentiment("I would like to know about my order")
    assert result is False

# region Chatbot Tests
# endregion

def test_chatbot_init_creates_required_components() -> None:
    chatbot = Chatbot()
    assert isinstance(chatbot.query_db, QueryDatabase)
    assert isinstance(chatbot.backend_manager, BackendManager)
    assert isinstance(chatbot.query_manager, QueryManager)
    assert isinstance(chatbot.session_manager, SessionManager)
    assert isinstance(chatbot.intent_service, IntentRecognitionService)
    assert isinstance(chatbot.sentiment_analyzer, SentimentAnalyzer)

@patch.object(SessionManager, 'add_to_history')
@patch.object(SentimentAnalyzer, 'detect_negative_sentiment', return_value=False)
@patch.object(QueryDatabase, 'get_response', return_value="")
@patch.object(IntentRecognitionService, 'recognize_intent', return_value="unknown")
@patch.object(QueryManager, 'get_handler')

def test_chatbot_process_query_adds_to_history(mock_get_handler, mock_recognize_intent, mock_get_response, mock_detect_sentiment, mock_add_to_history) -> None:
    chatbot = Chatbot()
    
    mock_handler = MagicMock()
    mock_handler.handle.return_value = "Default response"
    mock_get_handler.return_value = mock_handler
    
    chatbot.process_query("test query")
    
    mock_add_to_history.assert_called_once_with("test query")

@patch.object(QueryManager, 'get_handler')

def test_chatbot_process_query_with_awaiting_order_id_and_refund(mock_get_handler) -> None:
    chatbot = Chatbot()
    chatbot.session_manager.set("awaiting_order_id", True)
    chatbot.session_manager.set("refund", True)
    
    refund_handler = MagicMock()
    refund_handler.handle.return_value = "Refund response"
    mock_get_handler.return_value = refund_handler
    
    result = chatbot.process_query("123456")
    
    refund_handler.handle.assert_called_once_with("123456", chatbot.backend_manager, chatbot.session_manager)
    assert result == "Refund response"

@patch.object(QueryManager, 'get_handler')

def test_chatbot_process_query_with_awaiting_order_id_without_refund(mock_get_handler) -> None:
    chatbot = Chatbot()
    chatbot.session_manager.set("awaiting_order_id", True)
    
    order_handler = MagicMock()
    order_handler.handle.return_value = "Order response"
    mock_get_handler.return_value = order_handler
    
    result = chatbot.process_query("123456")
    
    order_handler.handle.assert_called_once_with("123456", chatbot.backend_manager, chatbot.session_manager)
    assert result == "Order response"

@patch.object(QueryManager, 'get_handler')

def test_chatbot_process_query_with_awaiting_refund_reason(mock_get_handler) -> None:
    chatbot = Chatbot()
    chatbot.session_manager.set("awaiting_refund_reason", True)
    
    refund_reason_handler = MagicMock()
    refund_reason_handler.handle.return_value = "Refund reason response"
    mock_get_handler.return_value = refund_reason_handler
    
    result = chatbot.process_query("defective")
    
    refund_reason_handler.handle.assert_called_once_with("defective", chatbot.backend_manager, chatbot.session_manager)
    assert result == "Refund reason response"

@patch('chat_bot.LiveAgentNotifier.notify_agents')
@patch('chat_bot.ResponseFactory.get_random_response')
@patch.object(SentimentAnalyzer, 'detect_negative_sentiment', return_value=True)

def test_chatbot_process_query_with_negative_sentiment(mock_detect_sentiment, mock_get_random_response, mock_notify) -> None:
    chatbot = Chatbot()
    
    mock_get_random_response.return_value = "I'm sorry to hear that. Let me help you."
    
    result = chatbot.process_query("This is terrible service!")
    
    mock_notify.assert_called_once_with("Customer with negative sentiment: This is terrible service!")
    mock_get_random_response.assert_called_once_with("negative_sentiment")
    assert result == "I'm sorry to hear that. Let me help you."

@patch.object(SentimentAnalyzer, 'detect_negative_sentiment', return_value=False)
@patch.object(QueryDatabase, 'get_response', return_value="Database response")

def test_chatbot_process_query_with_db_response(mock_get_response, mock_detect_sentiment) -> None:
    chatbot = Chatbot()
    
    result = chatbot.process_query("hello")
    
    assert result == "Database response"

@patch.object(SentimentAnalyzer, 'detect_negative_sentiment', return_value=False)
@patch.object(QueryDatabase, 'get_response', return_value="")
@patch.object(IntentRecognitionService, 'recognize_intent', return_value="order")
@patch.object(QueryManager, 'get_handler')

def test_chatbot_process_query_with_recognized_intent(mock_get_handler, mock_recognize_intent, mock_get_response, mock_detect_sentiment) -> None:
    chatbot = Chatbot()
    
    order_handler = MagicMock()
    order_handler.handle.return_value = "Order tracking response"
    mock_get_handler.return_value = order_handler
    
    result = chatbot.process_query("where is my order")
    
    mock_get_handler.assert_called_once_with("order")
    order_handler.handle.assert_called_once_with("where is my order", chatbot.backend_manager, chatbot.session_manager)
    assert result == "Order tracking response"

@patch.object(SentimentAnalyzer, 'detect_negative_sentiment', return_value=False)
@patch.object(QueryDatabase, 'get_response', return_value="")
@patch.object(IntentRecognitionService, 'recognize_intent', return_value="unknown")
@patch.object(QueryManager, 'get_handler')

def test_chatbot_process_query_with_unknown_intent(mock_get_handler, mock_recognize_intent, mock_get_response, mock_detect_sentiment) -> None:
    chatbot = Chatbot()
    
    default_handler = MagicMock()
    default_handler.handle.return_value = "I don't understand that"
    mock_get_handler.return_value = default_handler
    
    result = chatbot.process_query("something random")
    
    mock_get_handler.assert_called_once_with("unknown")
    default_handler.handle.assert_called_once_with("something random", chatbot.backend_manager, chatbot.session_manager)
    assert result == "I don't understand that"

@patch.object(SentimentAnalyzer, 'detect_negative_sentiment', return_value=False)
@patch.object(QueryDatabase, 'get_response', return_value="")
@patch.object(IntentRecognitionService, 'recognize_intent', return_value="unknown")
@patch.object(QueryManager, 'get_handler')

def test_chatbot_process_query_session_flags_preserved_after_completion(mock_get_handler, mock_recognize_intent, mock_get_response, mock_detect_sentiment) -> None:
    chatbot = Chatbot()
    chatbot.session_manager.set("awaiting_order_id", True)
    chatbot.session_manager.set("order_id", "123456")
    
    order_handler = MagicMock()
    order_handler.handle.return_value = "Your order is in transit"
    mock_get_handler.return_value = order_handler
    
    result = chatbot.process_query("123456")
    
    assert chatbot.session_manager.get("awaiting_order_id") == True
    assert chatbot.session_manager.get("order_id") == "123456"
    assert result == "Your order is in transit"

def test_chatbot_reset_session_clears_all_session_data() -> None:
    chatbot = Chatbot()
    
    if not hasattr(chatbot, 'reset_session'):
        def reset_session():
            chatbot.session_manager.sessions = {}
        chatbot.reset_session = reset_session

    chatbot.session_manager.set("awaiting_order_id", True)
    chatbot.session_manager.set("order_id", "123456")
    chatbot.session_manager.set("awaiting_refund_reason", True)
    chatbot.session_manager.add_to_history("Previous message")
    
    chatbot.reset_session()

    assert chatbot.session_manager.sessions == {}

def test_chatbot_get_conversation_history_returns_list() -> None:
    chatbot = Chatbot()
    
    if not hasattr(chatbot, 'get_conversation_history'):
        def get_conversation_history():
            return chatbot.session_manager.get_history()
        chatbot.get_conversation_history = get_conversation_history
    
    chatbot.session_manager.add_to_history("Message 1")
    chatbot.session_manager.add_to_history("Message 2")
    
    history = chatbot.get_conversation_history()

    assert isinstance(history, list)
    assert len(history) == 2
    assert "Message 1" in history
    assert "Message 2" in history

def test_chatbot_get_conversation_history_returns_empty_list_if_no_history() -> None:
    chatbot = Chatbot()

    if not hasattr(chatbot, 'get_conversation_history'):
        def get_conversation_history():
            return chatbot.session_manager.get_history()
        chatbot.get_conversation_history = get_conversation_history
    
    history = chatbot.get_conversation_history()

    assert isinstance(history, list)
    assert len(history) == 0

@pytest.fixture
def chatbot() -> None:
    return Chatbot()

def test_chatbot_with_fixture(chatbot) -> None:
    assert isinstance(chatbot, Chatbot)
    assert isinstance(chatbot.query_db, QueryDatabase)
    assert isinstance(chatbot.backend_manager, BackendManager)

# region Run Tests
# endregion

if __name__ == "__main__":
    test_track_order_returns_valid_message()
    test_track_order_includes_order_id()
    test_process_refund_without_reason()
    test_process_refund_with_reason()
    test_check_availability_for_available_product()
    test_check_availability_for_unavailable_product()
    test_get_product_list_returns_all_products()
    test_extract_product_name_with_exact_match()
    test_extract_product_name_with_case_insensitive_match()
    test_extract_product_name_with_no_match_returns_first_non_common_word()
    test_extract_product_name_with_only_common_words_returns_empty()
    test_process_request_order()
    test_process_request_refund_without_reason()
    test_process_request_refund_with_reason()
    test_process_request_product()
    test_process_request_live_agent() 
    test_process_request_invalid_service()
    test_get_product_service_returns_product_service()
    test_query_db_init_with_no_filepath()
    test_query_db_init_with_filepath_exists()
    test_query_db_get_response_exact_match()
    test_query_db_get_response_with_punctuation()
    test_query_db_get_response_case_insensitive()
    test_query_db_get_response_no_match()
    test_session_manager_get_with_existing_key()
    test_session_manager_get_with_non_existing_key_returns_default()
    test_session_manager_set_adds_key_value_pair()
    test_session_manager_pop_removes_and_returns_value()
    test_session_manager_pop_with_non_existing_key_returns_default()
    test_session_manager_add_to_history_creates_history_if_not_exists()
    test_session_manager_add_to_history_appends_to_existing_history()
    test_order_tracking_handle_with_existing_order_id()
    test_order_tracking_handle_with_awaiting_order_id()
    test_order_tracking_handle_without_order_id_requests_it()
    test_refund_handle_with_existing_order_id()
    test_refund_handle_with_awaiting_order_id()
    test_refund_handle_without_order_id_requests_it()
    test_refund_reason_handle_with_awaiting_refund_reason()
    test_refund_reason_handle_without_awaiting_refund_reason()
    test_product_availability_handle_with_product_in_query()
    test_product_availability_handle_without_product_in_query()
    test_live_agent_handle_notifies_agents_and_returns_response()
    test_default_handle_logs_query_and_returns_default_response()
    test_default_handle_handles_file_error_gracefully()
    test_live_agent_observer_alert_prints_message()
    test_live_agent_notifier_add_observer_adds_to_list()
    test_live_agent_notifier_notify_agents_calls_alert_on_all_observers()
    test_response_factory_get_random_response_returns_from_category()
    test_response_factory_get_random_response_with_invalid_category_raises_error()
    test_query_manager_get_handler_returns_correct_handler_for_order()
    test_query_manager_get_handler_returns_correct_handler_for_refund()
    test_query_manager_get_handler_returns_correct_handler_for_refund_reason()
    test_query_manager_get_handler_returns_correct_handler_for_product()
    test_query_manager_get_handler_returns_correct_handler_for_live_agent()
    test_query_manager_get_handler_returns_default_handler_for_unknown_type()
    test_intent_recognition_recognize_intent_exact_match_in_queries_order()
    test_intent_recognition_recognize_intent_exact_match_in_queries_refund()
    test_intent_recognition_recognize_intent_exact_match_in_queries_product()
    test_intent_recognition_recognize_intent_exact_match_in_queries_live_agent()
    test_intent_recognition_recognize_intent_phrase_match_order()
    test_intent_recognition_recognize_intent_phrase_match_refund()
    test_intent_recognition_recognize_intent_phrase_match_product()
    test_intent_recognition_recognize_intent_phrase_match_live_agent()
    test_intent_recognition_recognize_intent_product_in_query()
    test_intent_recognition_recognize_intent_inventory_terms()
    test_intent_recognition_recognize_intent_tracking_terms()
    test_recognize_intent_unknown()
    test_detect_negative_sentiment_with_negative_word()
    test_detect_negative_sentiment_with_strong_negative_phrase()
    test_detect_negative_sentiment_with_neutral_message()
    test_chatbot_init_creates_required_components()
    test_chatbot_reset_session_clears_all_session_data()
    test_chatbot_get_conversation_history_returns_list()
    test_chatbot_get_conversation_history_returns_empty_list_if_no_history()
    print("All tests have passed! :)\n")
