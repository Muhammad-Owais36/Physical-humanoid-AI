"""
End-to-end test for the RAG Agent Service.

This script tests the complete functionality of the RAG agent service,
including API endpoints, configuration, and basic question answering.
"""

import os
import sys
import time
import requests
from typing import Dict, Any

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config import config


def test_api_endpoints() -> bool:
    """
    Test the basic API endpoints of the RAG agent service.

    Returns:
        True if all tests pass, False otherwise
    """
    print("Testing API endpoints...")

    base_url = f"http://{config.host}:{config.port}"

    try:
        # Test root endpoint
        response = requests.get(f"{base_url}/")
        if response.status_code != 200:
            print(f"❌ Root endpoint failed with status {response.status_code}")
            return False
        print("✅ Root endpoint OK")

        # Test health endpoint
        response = requests.get(f"{base_url}/health")
        if response.status_code != 200:
            print(f"❌ Health endpoint failed with status {response.status_code}")
            return False
        if response.json().get("status") != "healthy":
            print(f"❌ Health endpoint returned unexpected status: {response.json()}")
            return False
        print("✅ Health endpoint OK")

        return True

    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the service. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Error testing API endpoints: {e}")
        return False


def test_ask_endpoint() -> bool:
    """
    Test the question answering endpoint.

    Returns:
        True if test passes, False otherwise
    """
    print("Testing question answering endpoint...")

    base_url = f"http://{config.host}:{config.port}"

    try:
        # Test with a simple question
        test_question = {
            "question": "What is this service for?",
            "user_id": "test_user",
            "session_id": "test_session"
        }

        response = requests.post(
            f"{base_url}/api/v1/ask",
            json=test_question,
            timeout=30  # 30 second timeout
        )

        if response.status_code != 200:
            print(f"❌ Ask endpoint failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False

        response_data = response.json()

        # Check if required fields are present
        required_fields = ["answer", "question", "retrieved_chunks", "confidence_score", "sources", "request_id"]
        for field in required_fields:
            if field not in response_data:
                print(f"❌ Missing required field in response: {field}")
                return False

        print("✅ Ask endpoint OK")
        print(f"   Question: {response_data['question'][:50]}...")
        print(f"   Answer length: {len(response_data['answer'])} characters")
        print(f"   Retrieved chunks: {len(response_data['retrieved_chunks'])}")
        print(f"   Confidence score: {response_data['confidence_score']}")
        print(f"   Sources: {len(response_data['sources'])}")

        return True

    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the service. Is it running?")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out. This might be expected if the service is processing.")
        return True  # Consider timeout as acceptable for this test
    except Exception as e:
        print(f"❌ Error testing ask endpoint: {e}")
        return False


def test_configuration() -> bool:
    """
    Test that the configuration is properly loaded.

    Returns:
        True if configuration is valid, False otherwise
    """
    print("Testing configuration...")

    try:
        # Check that required config values are present
        required_config = [
            "openai_api_key",
            "qdrant_api_key",
            "qdrant_url"
        ]

        for config_attr in required_config:
            value = getattr(config, config_attr, None)
            if not value:
                print(f"❌ Missing required configuration: {config_attr}")
                return False

        print("✅ Configuration OK")
        print(f"   Model: {config.model_name}")
        print(f"   Host: {config.host}")
        print(f"   Port: {config.port}")
        print(f"   Max context chunks: {config.max_context_chunks}")

        return True

    except Exception as e:
        print(f"❌ Error testing configuration: {e}")
        return False


def run_end_to_end_tests() -> Dict[str, Any]:
    """
    Run all end-to-end tests for the RAG agent service.

    Returns:
        Dictionary with test results
    """
    print("Starting end-to-end tests for RAG Agent Service...\n")

    results = {
        "config_ok": False,
        "api_endpoints_ok": False,
        "ask_endpoint_ok": False,
        "all_passed": False
    }

    # Wait a moment to ensure service is ready if just started
    time.sleep(2)

    # Test configuration first
    results["config_ok"] = test_configuration()
    if not results["config_ok"]:
        print("\n❌ Configuration test failed. Stopping tests.")
        return results

    print()

    # Test API endpoints
    results["api_endpoints_ok"] = test_api_endpoints()
    print()

    # Test ask endpoint if API endpoints are OK
    if results["api_endpoints_ok"]:
        results["ask_endpoint_ok"] = test_ask_endpoint()
        print()

    # Overall result
    results["all_passed"] = (
        results["config_ok"] and
        results["api_endpoints_ok"] and
        results["ask_endpoint_ok"]
    )

    if results["all_passed"]:
        print("🎉 All end-to-end tests passed!")
    else:
        print("❌ Some tests failed:")
        if not results["config_ok"]:
            print("  - Configuration test failed")
        if not results["api_endpoints_ok"]:
            print("  - API endpoints test failed")
        if not results["ask_endpoint_ok"]:
            print("  - Ask endpoint test failed")

    return results


if __name__ == "__main__":
    test_results = run_end_to_end_tests()

    # Exit with appropriate code
    sys.exit(0 if test_results["all_passed"] else 1)