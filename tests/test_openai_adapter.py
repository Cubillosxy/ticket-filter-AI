"""
Tests for OpenAI adapter using mocked HTTP responses
"""
from __future__ import annotations

import httpx
import pytest
from unittest.mock import Mock, patch

from app.adapters.ai.openai_adapter import OpenAIClassifier


@pytest.fixture
def classifier():
    """Create an OpenAI classifier instance for testing"""
    return OpenAIClassifier(
        api_key="test-api-key-123",
        model="gpt-4o-mini",
        timeout_ms=5000,
    )


@pytest.mark.asyncio
async def test_successful_classification(classifier):
    """Test successful OpenAI classification with valid JSON response"""
    mock_response_data = {
        "choices": [
            {
                "message": {
                    "content": '{"category": "Billing", "confidence": 0.95}'
                }
            }
        ]
    }
    
    # Create a proper mock response
    mock_response = Mock(spec=httpx.Response)
    mock_response.json = Mock(return_value=mock_response_data)
    mock_response.raise_for_status = Mock(return_value=None)
    
    # Mock the AsyncClient
    async def mock_post(*args, **kwargs):
        return mock_response
    
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = Mock()
        mock_client.post = mock_post
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        result = await classifier.classify("I need a refund for duplicate charge")
        
        assert result.category == "Billing"
        assert result.confidence == 0.95
        assert result.raw == mock_response_data


@pytest.mark.asyncio
async def test_classification_with_nested_json(classifier):
    """Test classification when JSON is deeply nested in response"""
    mock_response_data = {
        "id": "test-123",
        "object": "response",
        "data": {
            "choices": [
                {
                    "text": '{"category": "Technical Issue", "confidence": 0.88}'
                }
            ]
        }
    }
    
    mock_response = Mock(spec=httpx.Response)
    mock_response.json = Mock(return_value=mock_response_data)
    mock_response.raise_for_status = Mock(return_value=None)
    
    async def mock_post(*args, **kwargs):
        return mock_response
    
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = Mock()
        mock_client.post = mock_post
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        result = await classifier.classify("API returning 500 errors")
        
        assert result.category == "Technical Issue"
        assert result.confidence == 0.88


@pytest.mark.asyncio
async def test_classification_with_malformed_json(classifier):
    """Test classification falls back to defaults when JSON is malformed"""
    mock_response_data = {
        "choices": [
            {
                "message": {
                    "content": "This is not valid JSON at all"
                }
            }
        ]
    }
    
    mock_response = Mock(spec=httpx.Response)
    mock_response.json = Mock(return_value=mock_response_data)
    mock_response.raise_for_status = Mock(return_value=None)
    
    async def mock_post(*args, **kwargs):
        return mock_response
    
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = Mock()
        mock_client.post = mock_post
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        result = await classifier.classify("Some ticket text")
        
        # Should fall back to defaults
        assert result.category == "Other"
        assert result.confidence == 0.5


@pytest.mark.asyncio
async def test_confidence_clamping(classifier):
    """Test that confidence values are clamped to [0, 1] range"""
    mock_response_data = {
        "response": '{"category": "Account / Access", "confidence": 1.5}'
    }
    
    mock_response = Mock(spec=httpx.Response)
    mock_response.json = Mock(return_value=mock_response_data)
    mock_response.raise_for_status = Mock(return_value=None)
    
    async def mock_post(*args, **kwargs):
        return mock_response
    
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = Mock()
        mock_client.post = mock_post
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        result = await classifier.classify("Can't login to my account")
        
        assert result.category == "Account / Access"
        assert result.confidence == 1.0  # Should be clamped to 1.0


@pytest.mark.asyncio
async def test_http_error_propagates(classifier):
    """Test that HTTP errors are properly raised"""
    async def mock_post(*args, **kwargs):
        raise httpx.HTTPStatusError(
            "401 Unauthorized",
            request=Mock(),
            response=Mock(status_code=401)
        )
    
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = Mock()
        mock_client.post = mock_post
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        with pytest.raises(httpx.HTTPStatusError):
            await classifier.classify("Test ticket")


@pytest.mark.asyncio
async def test_timeout_error_propagates(classifier):
    """Test that timeout errors are properly raised"""
    async def mock_post(*args, **kwargs):
        raise httpx.TimeoutException("Request timed out")
    
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = Mock()
        mock_client.post = mock_post
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        with pytest.raises(httpx.TimeoutException):
            await classifier.classify("Test ticket")


@pytest.mark.asyncio
async def test_missing_category_defaults_to_other(classifier):
    """Test missing category field defaults to 'Other'"""
    mock_response_data = {
        "data": '{"confidence": 0.75}'  # Missing category
    }
    
    mock_response = Mock(spec=httpx.Response)
    mock_response.json = Mock(return_value=mock_response_data)
    mock_response.raise_for_status = Mock(return_value=None)
    
    async def mock_post(*args, **kwargs):
        return mock_response
    
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = Mock()
        mock_client.post = mock_post
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        result = await classifier.classify("Test ticket")
        
        assert result.category == "Other"
        assert result.confidence == 0.75
