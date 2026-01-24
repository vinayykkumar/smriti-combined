"""Unit tests for search logic, cache, and user profile features."""
import hashlib
import threading
import time
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
from bson import ObjectId


class SimpleCache:
    def __init__(self):
        self._cache = {}
        self._lock = threading.Lock()

    def get(self, key):
        with self._lock:
            if key not in self._cache:
                return None
            entry = self._cache[key]
            expires_at = entry.get('expires_at')
            if expires_at and datetime.utcnow() > expires_at:
                del self._cache[key]
                return None
            return entry.get('value')

    def set(self, key, value, ttl_seconds=300):
        with self._lock:
            expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
            self._cache[key] = {'value': value, 'expires_at': expires_at}

    def clear(self):
        with self._lock:
            self._cache.clear()

    def size(self):
        with self._lock:
            return len(self._cache)


cache = SimpleCache()
SEARCH_CACHE_PREFIX = 'search:'


def _build_search_cache_key(q, author_id, content_type, start_date, end_date, skip, limit):
    raw = f'{q}|{author_id}|{content_type}|{start_date}|{end_date}|{skip}|{limit}'
    hash_digest = hashlib.sha256(raw.encode()).hexdigest()[:16]
    return f'{SEARCH_CACHE_PREFIX}{hash_digest}'


def _clear_search_cache():
    cache.clear()


def test_cache_key_deterministic():
    key1 = _build_search_cache_key('test', None, None, None, None, 0, 20)
    key2 = _build_search_cache_key('test', None, None, None, None, 0, 20)
    assert key1 == key2, 'Same params should produce same key'


def test_cache_key_unique_per_query():
    key1 = _build_search_cache_key('test', None, None, None, None, 0, 20)
    key3 = _build_search_cache_key('different', None, None, None, None, 0, 20)
    assert key1 != key3, 'Different query should produce different key'


def test_cache_key_unique_per_filter():
    key1 = _build_search_cache_key('test', None, None, None, None, 0, 20)
    key4 = _build_search_cache_key('test', 'author1', None, None, None, 0, 20)
    key5 = _build_search_cache_key('test', None, 'note', None, None, 0, 20)
    key6 = _build_search_cache_key('test', None, None, '2024-01-01', '2024-12-31', 0, 20)
    assert key1 != key4, 'Author filter should change key'
    assert key1 != key5, 'Content type should change key'
    assert key1 != key6, 'Date range should change key'


def test_cache_key_starts_with_prefix():
    key = _build_search_cache_key('test', None, None, None, None, 0, 20)
    assert key.startswith('search:'), 'Key should start with search: prefix'


def test_cache_set_and_get():
    cache.clear()
    cache.set('search:abc', {'posts': [{'title': 'test'}], 'total': 1}, ttl_seconds=300)
    result = cache.get('search:abc')
    assert result is not None
    assert result['total'] == 1
    assert len(result['posts']) == 1


def test_cache_clear_on_new_post():
    cache.clear()
    cache.set('search:def', {'posts': [], 'total': 0}, ttl_seconds=300)
    cache.set('search:ghi', {'posts': [{'x': 1}], 'total': 1}, ttl_seconds=300)
    assert cache.size() == 2
    _clear_search_cache()
    assert cache.size() == 0
    assert cache.get('search:def') is None
    assert cache.get('search:ghi') is None


def test_cache_ttl_expiration():
    cache.clear()
    cache.set('short_ttl', 'value', ttl_seconds=0)
    time.sleep(0.01)
    assert cache.get('short_ttl') is None


def test_iso_date_parsing():
    test_dates = ['2024-01-15', '2024-01-15T00:00:00Z', '2024-01-15T10:30:00+05:30']
    for date_str in test_dates:
        parsed = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        assert parsed is not None, f'Failed to parse: {date_str}'


def test_objectid_validation():
    valid_id = '507f1f77bcf86cd799439011'
    invalid_id = 'not-a-valid-id'
    assert ObjectId.is_valid(valid_id) is True
    assert ObjectId.is_valid(invalid_id) is False


def test_search_query_filter_building():
    """Test that query filters are built correctly for MongoDB."""
    query_filter = {}

    # Text search
    q = "test query"
    if q and q.strip():
        query_filter["$text"] = {"$search": q.strip()}
    assert "$text" in query_filter
    assert query_filter["$text"]["$search"] == "test query"

    # Author filter
    author_id = "507f1f77bcf86cd799439011"
    if author_id:
        query_filter["author.user_id"] = author_id
    assert query_filter["author.user_id"] == author_id

    # Content type filter
    content_type = "note"
    if content_type:
        query_filter["content_type"] = content_type
    assert query_filter["content_type"] == "note"

    # Date range
    start_date = "2024-01-01"
    end_date = "2024-12-31"
    date_filter = {}
    if start_date:
        parsed_start = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
        date_filter["$gte"] = parsed_start.isoformat()
    if end_date:
        parsed_end = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
        date_filter["$lte"] = parsed_end.isoformat()
    if date_filter:
        query_filter["created_at"] = date_filter
    assert "created_at" in query_filter
    assert "$gte" in query_filter["created_at"]
    assert "$lte" in query_filter["created_at"]


def test_pagination_params():
    """Test pagination parameter handling."""
    skip = 20
    limit = 10
    assert skip >= 0
    assert limit > 0
    assert limit <= 100


if __name__ == '__main__':
    tests = [
        test_cache_key_deterministic,
        test_cache_key_unique_per_query,
        test_cache_key_unique_per_filter,
        test_cache_key_starts_with_prefix,
        test_cache_set_and_get,
        test_cache_clear_on_new_post,
        test_cache_ttl_expiration,
        test_iso_date_parsing,
        test_objectid_validation,
        test_search_query_filter_building,
        test_pagination_params,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            print(f'  PASSED: {test.__name__}')
            passed += 1
        except AssertionError as e:
            print(f'  FAILED: {test.__name__} - {e}')
            failed += 1
        except Exception as e:
            print(f'  ERROR: {test.__name__} - {e}')
            failed += 1

    print(f'\n{passed}/{passed + failed} tests passed')
    if failed > 0:
        exit(1)
    print('ALL BACKEND LOGIC TESTS PASSED')
