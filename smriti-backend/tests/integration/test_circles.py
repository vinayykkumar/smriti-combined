"""
Integration tests for Circles (Sangha) feature.

Tests real user flows:
- User A creates circle, User B joins, User A posts, User B sees it
- Non-member cannot view circle posts
- Deletion vote flow
- Circle limits

NOTE: These tests require MongoDB to be running.
Run with: pytest tests/integration/test_circles.py -v
Skip with: pytest tests/integration/test_circles.py -v -m "not integration"
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from bson import ObjectId
from datetime import datetime
import asyncio

from app.main import app
from app.database.connection import db as database, get_database
from app.utils.security import create_access_token
from app.circles.constants import MAX_MEMBERS_PER_CIRCLE, MAX_CIRCLES_PER_USER


# Check if MongoDB is available
def mongodb_available():
    """Check if MongoDB is available for integration tests."""
    try:
        from pymongo import MongoClient
        from app.config.settings import settings
        client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=2000)
        client.server_info()
        return True
    except Exception:
        return False


# Skip all tests if MongoDB not available
pytestmark = pytest.mark.skipif(
    not mongodb_available(),
    reason="MongoDB not available - skipping integration tests"
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def anyio_backend():
    return 'asyncio'


@pytest_asyncio.fixture
async def test_db():
    """Get test database connection."""
    # Connect if not already connected
    if database.client is None:
        database.connect()
    db = await get_database()
    yield db
    # Cleanup after tests
    await db.users.delete_many({"username": {"$regex": "^test_"}})
    await db.circles.delete_many({"name": {"$regex": "^Test Circle"}})
    await db.posts.delete_many({"author.username": {"$regex": "^test_"}})


@pytest_asyncio.fixture
async def user_a(test_db):
    """Create User A for testing."""
    user_doc = {
        "_id": ObjectId(),
        "username": f"test_user_a_{ObjectId()}",
        "email": f"test_a_{ObjectId()}@example.com",
        "hashed_password": "hashed",
        "created_at": datetime.utcnow().isoformat(),
        "email_verified": False,
        "phone_verified": False
    }
    await test_db.users.insert_one(user_doc)
    token = create_access_token(subject=str(user_doc["_id"]))
    return {
        "id": str(user_doc["_id"]),
        "username": user_doc["username"],
        "token": token
    }


@pytest_asyncio.fixture
async def user_b(test_db):
    """Create User B for testing."""
    user_doc = {
        "_id": ObjectId(),
        "username": f"test_user_b_{ObjectId()}",
        "email": f"test_b_{ObjectId()}@example.com",
        "hashed_password": "hashed",
        "created_at": datetime.utcnow().isoformat(),
        "email_verified": False,
        "phone_verified": False
    }
    await test_db.users.insert_one(user_doc)
    token = create_access_token(subject=str(user_doc["_id"]))
    return {
        "id": str(user_doc["_id"]),
        "username": user_doc["username"],
        "token": token
    }


@pytest_asyncio.fixture
async def user_c(test_db):
    """Create User C (non-member) for testing."""
    user_doc = {
        "_id": ObjectId(),
        "username": f"test_user_c_{ObjectId()}",
        "email": f"test_c_{ObjectId()}@example.com",
        "hashed_password": "hashed",
        "created_at": datetime.utcnow().isoformat(),
        "email_verified": False,
        "phone_verified": False
    }
    await test_db.users.insert_one(user_doc)
    token = create_access_token(subject=str(user_doc["_id"]))
    return {
        "id": str(user_doc["_id"]),
        "username": user_doc["username"],
        "token": token
    }


@pytest_asyncio.fixture
async def client():
    """Create async HTTP client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


def auth_header(token: str) -> dict:
    """Create authorization header."""
    return {"Authorization": f"Bearer {token}"}


# =============================================================================
# MAIN USER FLOW TEST
# =============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
async def test_complete_circle_flow(client, test_db, user_a, user_b, user_c):
    """
    Test the complete circle flow:
    1. User A creates a circle
    2. User A gets the invite code
    3. User B joins via invite code
    4. User A creates a post in the circle
    5. User B can see the post
    6. User C (non-member) cannot see the post
    """
    # Step 1: User A creates a circle
    create_response = await client.post(
        "/api/v1/circles/",
        json={
            "name": "Test Circle Family",
            "description": "A test circle for integration tests",
            "color": "#7986CB"
        },
        headers=auth_header(user_a["token"])
    )
    assert create_response.status_code == 201
    circle_data = create_response.json()["data"]["circle"]
    circle_id = circle_data["circleId"]
    invite_code = circle_data["inviteCode"]

    assert circle_data["name"] == "Test Circle Family"
    assert circle_data["memberCount"] == 1
    assert len(invite_code) == 8

    # Step 2: User B previews the circle
    preview_response = await client.get(
        f"/api/v1/circles/preview/{invite_code}",
        headers=auth_header(user_b["token"])
    )
    assert preview_response.status_code == 200
    preview_data = preview_response.json()["data"]["circle"]
    assert preview_data["name"] == "Test Circle Family"
    assert preview_data["isFull"] is False
    assert preview_data["alreadyMember"] is False

    # Step 3: User B joins the circle
    join_response = await client.post(
        "/api/v1/circles/join",
        json={"inviteCode": invite_code},
        headers=auth_header(user_b["token"])
    )
    assert join_response.status_code == 201
    joined_circle = join_response.json()["data"]["circle"]
    assert joined_circle["memberCount"] == 2

    # Verify User B is now a member
    members = joined_circle["members"]
    member_ids = [m["userId"] for m in members]
    assert user_a["id"] in member_ids
    assert user_b["id"] in member_ids

    # Step 4: User A creates a post in the circle
    post_response = await client.post(
        f"/api/v1/circles/{circle_id}/posts",
        data={
            "content_type": "note",
            "text_content": "Hello my circle! This is a secret message."
        },
        headers=auth_header(user_a["token"])
    )
    assert post_response.status_code == 201
    post_data = post_response.json()["data"]["post"]
    assert post_data["textContent"] == "Hello my circle! This is a secret message."
    assert post_data["visibility"] == "circles"

    # Step 5: User B can see the post
    feed_response = await client.get(
        f"/api/v1/circles/{circle_id}/posts",
        headers=auth_header(user_b["token"])
    )
    assert feed_response.status_code == 200
    feed_data = feed_response.json()["data"]
    assert feed_data["total"] == 1
    assert len(feed_data["posts"]) == 1
    assert feed_data["posts"][0]["textContent"] == "Hello my circle! This is a secret message."

    # Step 6: User C (non-member) cannot see the posts
    non_member_response = await client.get(
        f"/api/v1/circles/{circle_id}/posts",
        headers=auth_header(user_c["token"])
    )
    assert non_member_response.status_code == 403
    assert non_member_response.json()["detail"]["code"] == "NOT_CIRCLE_MEMBER"


# =============================================================================
# CIRCLE CREATION TESTS
# =============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_circle_success(client, test_db, user_a):
    """Test successful circle creation."""
    response = await client.post(
        "/api/v1/circles/",
        json={
            "name": "Test Circle New",
            "description": "My test circle",
            "color": "#EF5350",
            "emoji": "🎯"
        },
        headers=auth_header(user_a["token"])
    )
    assert response.status_code == 201
    data = response.json()["data"]["circle"]

    assert data["name"] == "Test Circle New"
    assert data["description"] == "My test circle"
    assert data["color"] == "#EF5350"
    assert data["emoji"] == "🎯"
    assert data["memberCount"] == 1
    assert data["maxMembers"] == MAX_MEMBERS_PER_CIRCLE
    assert len(data["inviteCode"]) == 8
    assert data["createdBy"]["userId"] == user_a["id"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_circle_minimal(client, test_db, user_a):
    """Test creating circle with just a name."""
    response = await client.post(
        "/api/v1/circles/",
        json={"name": "Test Circle Minimal"},
        headers=auth_header(user_a["token"])
    )
    assert response.status_code == 201
    data = response.json()["data"]["circle"]
    assert data["name"] == "Test Circle Minimal"
    assert data["color"] is not None  # Should have random color


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_circle_invalid_color(client, test_db, user_a):
    """Test that invalid color is rejected."""
    response = await client.post(
        "/api/v1/circles/",
        json={
            "name": "Test Circle BadColor",
            "color": "#FFFFFF"  # Not in palette
        },
        headers=auth_header(user_a["token"])
    )
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_circle_requires_auth(client, test_db):
    """Test that creating circle requires authentication."""
    response = await client.post(
        "/api/v1/circles/",
        json={"name": "Test Circle NoAuth"}
    )
    assert response.status_code == 401


# =============================================================================
# CIRCLE LIST AND DETAILS TESTS
# =============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_circles(client, test_db, user_a):
    """Test listing user's circles."""
    # Create two circles
    await client.post(
        "/api/v1/circles/",
        json={"name": "Test Circle List 1"},
        headers=auth_header(user_a["token"])
    )
    await client.post(
        "/api/v1/circles/",
        json={"name": "Test Circle List 2"},
        headers=auth_header(user_a["token"])
    )

    response = await client.get(
        "/api/v1/circles/",
        headers=auth_header(user_a["token"])
    )
    assert response.status_code == 200
    data = response.json()["data"]

    assert data["total"] >= 2
    # List items should not include invite code
    for circle in data["circles"]:
        assert "inviteCode" not in circle


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_circle_details(client, test_db, user_a):
    """Test getting full circle details."""
    # Create circle
    create_response = await client.post(
        "/api/v1/circles/",
        json={"name": "Test Circle Details"},
        headers=auth_header(user_a["token"])
    )
    circle_id = create_response.json()["data"]["circle"]["circleId"]

    # Get details
    response = await client.get(
        f"/api/v1/circles/{circle_id}",
        headers=auth_header(user_a["token"])
    )
    assert response.status_code == 200
    data = response.json()["data"]["circle"]

    assert data["name"] == "Test Circle Details"
    assert "inviteCode" in data  # Full details include invite code
    assert "members" in data


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_circle_non_member_denied(client, test_db, user_a, user_c):
    """Test that non-member cannot get circle details."""
    # Create circle as user A
    create_response = await client.post(
        "/api/v1/circles/",
        json={"name": "Test Circle Private"},
        headers=auth_header(user_a["token"])
    )
    circle_id = create_response.json()["data"]["circle"]["circleId"]

    # User C tries to access
    response = await client.get(
        f"/api/v1/circles/{circle_id}",
        headers=auth_header(user_c["token"])
    )
    assert response.status_code == 404


# =============================================================================
# JOIN CIRCLE TESTS
# =============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
async def test_join_circle_success(client, test_db, user_a, user_b):
    """Test joining a circle with valid invite code."""
    # Create circle
    create_response = await client.post(
        "/api/v1/circles/",
        json={"name": "Test Circle Join"},
        headers=auth_header(user_a["token"])
    )
    invite_code = create_response.json()["data"]["circle"]["inviteCode"]

    # User B joins
    response = await client.post(
        "/api/v1/circles/join",
        json={"inviteCode": invite_code},
        headers=auth_header(user_b["token"])
    )
    assert response.status_code == 201
    assert response.json()["data"]["circle"]["memberCount"] == 2


@pytest.mark.asyncio
@pytest.mark.integration
async def test_join_circle_invalid_code(client, test_db, user_b):
    """Test joining with invalid invite code."""
    response = await client.post(
        "/api/v1/circles/join",
        json={"inviteCode": "INVALID8"},
        headers=auth_header(user_b["token"])
    )
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "INVALID_INVITE_CODE"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_join_circle_already_member(client, test_db, user_a):
    """Test that creator cannot rejoin their own circle."""
    # Create circle
    create_response = await client.post(
        "/api/v1/circles/",
        json={"name": "Test Circle Rejoin"},
        headers=auth_header(user_a["token"])
    )
    invite_code = create_response.json()["data"]["circle"]["inviteCode"]

    # User A tries to join again
    response = await client.post(
        "/api/v1/circles/join",
        json={"inviteCode": invite_code},
        headers=auth_header(user_a["token"])
    )
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "ALREADY_MEMBER"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_join_circle_code_with_spaces(client, test_db, user_a, user_b):
    """Test that invite code with spaces is normalized."""
    # Create circle
    create_response = await client.post(
        "/api/v1/circles/",
        json={"name": "Test Circle Spaces"},
        headers=auth_header(user_a["token"])
    )
    invite_code = create_response.json()["data"]["circle"]["inviteCode"]

    # Add spaces to the code
    spaced_code = f"{invite_code[:4]} {invite_code[4:]}"

    response = await client.post(
        "/api/v1/circles/join",
        json={"inviteCode": spaced_code},
        headers=auth_header(user_b["token"])
    )
    assert response.status_code == 201


# =============================================================================
# CIRCLE FEED TESTS
# =============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
async def test_circle_feed_pagination(client, test_db, user_a):
    """Test circle feed pagination."""
    # Create circle
    create_response = await client.post(
        "/api/v1/circles/",
        json={"name": "Test Circle Pagination"},
        headers=auth_header(user_a["token"])
    )
    circle_id = create_response.json()["data"]["circle"]["circleId"]

    # Create 5 posts
    for i in range(5):
        await client.post(
            f"/api/v1/circles/{circle_id}/posts",
            data={
                "content_type": "note",
                "text_content": f"Post number {i+1}"
            },
            headers=auth_header(user_a["token"])
        )

    # Get first page (2 posts)
    response = await client.get(
        f"/api/v1/circles/{circle_id}/posts?limit=2&skip=0",
        headers=auth_header(user_a["token"])
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total"] == 5
    assert len(data["posts"]) == 2

    # Get second page
    response2 = await client.get(
        f"/api/v1/circles/{circle_id}/posts?limit=2&skip=2",
        headers=auth_header(user_a["token"])
    )
    data2 = response2.json()["data"]
    assert len(data2["posts"]) == 2

    # Posts should be in reverse chronological order (newest first)
    # So skip=0 should have newer posts than skip=2


@pytest.mark.asyncio
@pytest.mark.integration
async def test_circle_feed_sorts_by_time(client, test_db, user_a):
    """Test that circle feed is sorted by time (newest first)."""
    # Create circle
    create_response = await client.post(
        "/api/v1/circles/",
        json={"name": "Test Circle Sort"},
        headers=auth_header(user_a["token"])
    )
    circle_id = create_response.json()["data"]["circle"]["circleId"]

    # Create posts
    await client.post(
        f"/api/v1/circles/{circle_id}/posts",
        data={"content_type": "note", "text_content": "First post"},
        headers=auth_header(user_a["token"])
    )
    await asyncio.sleep(0.1)  # Small delay to ensure different timestamps
    await client.post(
        f"/api/v1/circles/{circle_id}/posts",
        data={"content_type": "note", "text_content": "Second post"},
        headers=auth_header(user_a["token"])
    )

    response = await client.get(
        f"/api/v1/circles/{circle_id}/posts",
        headers=auth_header(user_a["token"])
    )
    posts = response.json()["data"]["posts"]

    # Newest first
    assert posts[0]["textContent"] == "Second post"
    assert posts[1]["textContent"] == "First post"


# =============================================================================
# DELETION VOTE TESTS
# =============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
async def test_deletion_vote_flow(client, test_db, user_a, user_b):
    """Test the deletion vote flow."""
    # Create circle
    create_response = await client.post(
        "/api/v1/circles/",
        json={"name": "Test Circle Delete"},
        headers=auth_header(user_a["token"])
    )
    circle_id = create_response.json()["data"]["circle"]["circleId"]
    invite_code = create_response.json()["data"]["circle"]["inviteCode"]

    # User B joins
    await client.post(
        "/api/v1/circles/join",
        json={"inviteCode": invite_code},
        headers=auth_header(user_b["token"])
    )

    # User A votes to delete
    vote_response = await client.post(
        f"/api/v1/circles/{circle_id}/vote-delete",
        headers=auth_header(user_a["token"])
    )
    assert vote_response.status_code == 200
    vote_data = vote_response.json()["data"]
    assert vote_data["votesCast"] == 1
    assert vote_data["votesNeeded"] == 2
    assert vote_data["yourVote"] is True
    assert vote_data["deleted"] is False

    # Circle should still exist
    details_response = await client.get(
        f"/api/v1/circles/{circle_id}",
        headers=auth_header(user_a["token"])
    )
    assert details_response.status_code == 200

    # User B votes - should trigger deletion (unanimous)
    delete_response = await client.post(
        f"/api/v1/circles/{circle_id}/vote-delete",
        headers=auth_header(user_b["token"])
    )
    assert delete_response.status_code == 200
    delete_data = delete_response.json()["data"]
    assert delete_data["deleted"] is True

    # Circle should be gone
    gone_response = await client.get(
        f"/api/v1/circles/{circle_id}",
        headers=auth_header(user_a["token"])
    )
    assert gone_response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_revoke_deletion_vote(client, test_db, user_a, user_b):
    """Test revoking a deletion vote."""
    # Create circle
    create_response = await client.post(
        "/api/v1/circles/",
        json={"name": "Test Circle Revoke"},
        headers=auth_header(user_a["token"])
    )
    circle_id = create_response.json()["data"]["circle"]["circleId"]
    invite_code = create_response.json()["data"]["circle"]["inviteCode"]

    # User B joins
    await client.post(
        "/api/v1/circles/join",
        json={"inviteCode": invite_code},
        headers=auth_header(user_b["token"])
    )

    # User A votes
    await client.post(
        f"/api/v1/circles/{circle_id}/vote-delete",
        headers=auth_header(user_a["token"])
    )

    # User A revokes vote
    revoke_response = await client.delete(
        f"/api/v1/circles/{circle_id}/vote-delete",
        headers=auth_header(user_a["token"])
    )
    assert revoke_response.status_code == 200
    assert revoke_response.json()["data"]["yourVote"] is False
    assert revoke_response.json()["data"]["votesCast"] == 0


# =============================================================================
# UPDATE CIRCLE TESTS
# =============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_circle(client, test_db, user_a):
    """Test updating circle details."""
    # Create circle
    create_response = await client.post(
        "/api/v1/circles/",
        json={"name": "Test Circle Update"},
        headers=auth_header(user_a["token"])
    )
    circle_id = create_response.json()["data"]["circle"]["circleId"]

    # Update
    response = await client.patch(
        f"/api/v1/circles/{circle_id}",
        json={
            "name": "Test Circle Updated Name",
            "description": "New description"
        },
        headers=auth_header(user_a["token"])
    )
    assert response.status_code == 200
    data = response.json()["data"]["circle"]
    assert data["name"] == "Test Circle Updated Name"
    assert data["description"] == "New description"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_any_member_can_update(client, test_db, user_a, user_b):
    """Test that any member can update the circle (not just creator)."""
    # Create circle as user A
    create_response = await client.post(
        "/api/v1/circles/",
        json={"name": "Test Circle AnyUpdate"},
        headers=auth_header(user_a["token"])
    )
    circle_id = create_response.json()["data"]["circle"]["circleId"]
    invite_code = create_response.json()["data"]["circle"]["inviteCode"]

    # User B joins
    await client.post(
        "/api/v1/circles/join",
        json={"inviteCode": invite_code},
        headers=auth_header(user_b["token"])
    )

    # User B updates (should work - no admins!)
    response = await client.patch(
        f"/api/v1/circles/{circle_id}",
        json={"name": "Test Circle B Updated"},
        headers=auth_header(user_b["token"])
    )
    assert response.status_code == 200
    assert response.json()["data"]["circle"]["name"] == "Test Circle B Updated"


# =============================================================================
# REGENERATE INVITE CODE TESTS
# =============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
async def test_regenerate_invite_code(client, test_db, user_a, user_c):
    """Test regenerating invite code."""
    # Create circle
    create_response = await client.post(
        "/api/v1/circles/",
        json={"name": "Test Circle Regen"},
        headers=auth_header(user_a["token"])
    )
    circle_id = create_response.json()["data"]["circle"]["circleId"]
    old_code = create_response.json()["data"]["circle"]["inviteCode"]

    # Regenerate
    response = await client.post(
        f"/api/v1/circles/{circle_id}/regenerate-invite",
        headers=auth_header(user_a["token"])
    )
    assert response.status_code == 200
    new_code = response.json()["data"]["inviteCode"]
    assert new_code != old_code
    assert len(new_code) == 8

    # Old code should not work
    old_join_response = await client.post(
        "/api/v1/circles/join",
        json={"inviteCode": old_code},
        headers=auth_header(user_c["token"])
    )
    assert old_join_response.status_code == 404

    # New code should work
    new_join_response = await client.post(
        "/api/v1/circles/join",
        json={"inviteCode": new_code},
        headers=auth_header(user_c["token"])
    )
    assert new_join_response.status_code == 201


# =============================================================================
# CIRCLE POST VISIBILITY TESTS
# =============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
async def test_circle_post_not_in_public_feed(client, test_db, user_a, user_c):
    """Test that circle posts don't appear in the public feed."""
    # Create circle
    create_response = await client.post(
        "/api/v1/circles/",
        json={"name": "Test Circle Hidden"},
        headers=auth_header(user_a["token"])
    )
    circle_id = create_response.json()["data"]["circle"]["circleId"]

    # Create post in circle
    await client.post(
        f"/api/v1/circles/{circle_id}/posts",
        data={
            "content_type": "note",
            "text_content": "This is a secret circle post"
        },
        headers=auth_header(user_a["token"])
    )

    # Check public feed as user C
    public_response = await client.get(
        "/api/v1/posts/",
        headers=auth_header(user_c["token"])
    )
    assert public_response.status_code == 200
    posts = public_response.json()["data"]["posts"]

    # The circle post should NOT be in the public feed
    for post in posts:
        assert post.get("textContent") != "This is a secret circle post"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_non_member_cannot_post_to_circle(client, test_db, user_a, user_c):
    """Test that non-member cannot create posts in a circle."""
    # Create circle as user A
    create_response = await client.post(
        "/api/v1/circles/",
        json={"name": "Test Circle NoPost"},
        headers=auth_header(user_a["token"])
    )
    circle_id = create_response.json()["data"]["circle"]["circleId"]

    # User C (non-member) tries to post
    response = await client.post(
        f"/api/v1/circles/{circle_id}/posts",
        data={
            "content_type": "note",
            "text_content": "Sneaky post attempt"
        },
        headers=auth_header(user_c["token"])
    )
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "NOT_CIRCLE_MEMBER"
