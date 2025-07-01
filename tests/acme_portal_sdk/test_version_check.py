"""Test Python version compatibility checking functionality."""

import sys
from unittest.mock import patch

import pytest

from acme_portal_sdk.version_check import (
    get_python_version,
    get_required_python_version,
    is_python_version_compatible,
    get_version_info_message,
    check_compatibility_and_warn,
)


def test_get_python_version():
    """Test that get_python_version returns the current Python version."""
    version = get_python_version()
    assert len(version) == 3
    assert all(isinstance(v, int) for v in version)
    assert version == sys.version_info[:3]


def test_get_required_python_version():
    """Test that get_required_python_version returns expected minimum version."""
    version = get_required_python_version()
    assert version == (3, 9)


def test_is_python_version_compatible_with_current():
    """Test compatibility check with current Python version."""
    # Current version should always be compatible with itself
    current_version = sys.version_info[:2]
    assert is_python_version_compatible(current_version) is True


def test_is_python_version_compatible_with_old_version():
    """Test compatibility check with an old version."""
    # Should be incompatible with very old Python
    old_version = (3, 6)
    assert is_python_version_compatible(old_version) is True  # Current is newer


def test_is_python_version_compatible_with_future_version():
    """Test compatibility check with a future version."""
    # Should be incompatible with future Python versions  
    future_version = (4, 0)
    assert is_python_version_compatible(future_version) is False


def test_is_python_version_compatible_default():
    """Test compatibility check with default requirements."""
    # With Python 3.9 requirement, current version should be compatible
    assert is_python_version_compatible() is True


def test_get_version_info_message():
    """Test version info message generation."""
    message = get_version_info_message()
    assert "Python Version Check:" in message
    assert "Current version:" in message
    assert "Required version:" in message
    assert "Status:" in message
    assert ("✓ Compatible" in message or "✗ Incompatible" in message)


@patch('sys.version_info', (3, 8, 0))
def test_check_compatibility_and_warn_incompatible(capsys):
    """Test warning output for incompatible version."""
    result = check_compatibility_and_warn()
    assert result is False
    
    captured = capsys.readouterr()
    assert "WARNING: Incompatible Python version detected!" in captured.err
    assert "3.8.0" in captured.err
    assert "3.9+" in captured.err


def test_check_compatibility_and_warn_compatible():
    """Test no warning for compatible version."""
    # Current version should be compatible
    result = check_compatibility_and_warn()
    assert result is True


if __name__ == "__main__":
    pytest.main([__file__])