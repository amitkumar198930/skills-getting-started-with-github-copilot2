"""Test suite for Activity Signup API using AAA (Arrange-Act-Assert) pattern."""
import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client, fresh_activities):
        """
        Arrange: Fresh activities already set up by fixture
        Act: Fetch all activities
        Assert: Verify response code and data structure
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_get_activities_includes_participant_data(self, client, fresh_activities):
        """
        Arrange: Activities with known participants
        Act: Fetch activities
        Assert: Verify participant lists are returned
        """
        # Act
        response = client.get("/activities")

        # Assert
        data = response.json()
        assert "participants" in data["Chess Club"]
        assert "alice@mergington.edu" in data["Chess Club"]["participants"]
        assert len(data["Programming Class"]["participants"]) == 0

    def test_get_activities_includes_metadata(self, client, fresh_activities):
        """
        Arrange: Activities with metadata
        Act: Fetch activities
        Assert: Verify all required fields are present
        """
        # Act
        response = client.get("/activities")

        # Assert
        data = response.json()
        chess = data["Chess Club"]
        assert "description" in chess
        assert "schedule" in chess
        assert "max_participants" in chess
        assert chess["max_participants"] == 2


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_for_activity_success(self, client, fresh_activities):
        """
        Arrange: Activity exists with available spots
        Act: Post signup request with valid data
        Assert: Verify success and participant added to activity
        """
        # Arrange
        activity_name = "Programming Class"
        email = "bob@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert email in fresh_activities[activity_name]["participants"]
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    def test_signup_duplicate_email_returns_400(self, client, fresh_activities):
        """
        Arrange: Alice already signed up for Chess Club
        Act: Try to signup with duplicate email
        Assert: Verify 400 error with appropriate message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "alice@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
        assert len(fresh_activities[activity_name]["participants"]) == 1

    def test_signup_full_activity_returns_400(self, client, fresh_activities):
        """
        Arrange: Gym Class is at max capacity (2/2)
        Act: Try to signup when activity is full
        Assert: Verify 400 error with full activity message
        """
        # Arrange
        activity_name = "Gym Class"
        email = "charlie@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "full" in response.json()["detail"].lower()
        assert len(fresh_activities[activity_name]["participants"]) == 2

    def test_signup_nonexistent_activity_returns_404(self, client, fresh_activities):
        """
        Arrange: Activity does not exist
        Act: Try to signup for non-existent activity
        Assert: Verify 404 error
        """
        # Arrange
        activity_name = "Nonexistent Club"
        email = "bob@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_invalid_email_returns_400(self, client, fresh_activities):
        """
        Arrange: Invalid email without @ symbol
        Act: Try to signup with invalid email
        Assert: Verify 400 error
        """
        # Arrange
        activity_name = "Programming Class"
        email = "notanemail"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "Invalid email" in response.json()["detail"]

    def test_signup_empty_email_returns_400(self, client, fresh_activities):
        """
        Arrange: Empty email string
        Act: Try to signup with empty email
        Assert: Verify 400 error
        """
        # Arrange
        activity_name = "Programming Class"
        email = ""

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "Invalid email" in response.json()["detail"]

    def test_signup_normalizes_email_case(self, client, fresh_activities):
        """
        Arrange: Activity and email with different casing
        Act: Signup with uppercase email when lowercase already registered
        Assert: Verify duplicate detection works across cases
        """
        # Arrange
        activity_name = "Programming Class"
        email_lower = "bob@mergington.edu"
        email_upper = "BOB@MERGINGTON.EDU"

        # Act - First signup with lowercase
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email_lower}
        )

        # Act - Second signup with uppercase
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email_upper}
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_strips_whitespace(self, client, fresh_activities):
        """
        Arrange: Email with leading/trailing whitespace
        Act: Signup with whitespace-padded email
        Assert: Verify whitespace is handled and duplicate is detected
        """
        # Arrange
        activity_name = "Programming Class"
        email_clean = "bob@mergington.edu"
        email_padded = "  bob@mergington.edu  "

        # Act - First signup with clean email
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email_clean}
        )

        # Act - Second signup with padded email
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email_padded}
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/signup/{email} endpoint."""

    def test_remove_participant_success(self, client, fresh_activities):
        """
        Arrange: Alice is signed up for Chess Club
        Act: Delete participant
        Assert: Verify success and participant removed
        """
        # Arrange
        activity_name = "Chess Club"
        email = "alice@mergington.edu"
        assert len(fresh_activities[activity_name]["participants"]) == 1

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup/{email}"
        )

        # Assert
        assert response.status_code == 200
        assert email not in fresh_activities[activity_name]["participants"]
        assert len(fresh_activities[activity_name]["participants"]) == 0

    def test_remove_nonexistent_participant_returns_404(self, client, fresh_activities):
        """
        Arrange: Dave is not signed up for Chess Club
        Act: Try to delete non-existent participant
        Assert: Verify 404 error
        """
        # Arrange
        activity_name = "Chess Club"
        email = "dave@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup/{email}"
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_remove_participant_nonexistent_activity_returns_404(self, client, fresh_activities):
        """
        Arrange: Activity does not exist
        Act: Try to delete participant from non-existent activity
        Assert: Verify 404 error for activity not found
        """
        # Arrange
        activity_name = "Nonexistent Club"
        email = "alice@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup/{email}"
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_remove_participant_case_insensitive(self, client, fresh_activities):
        """
        Arrange: Alice signed up with lowercase email
        Act: Delete with uppercase email
        Assert: Verify case-insensitive removal works
        """
        # Arrange
        activity_name = "Chess Club"
        email_lower = "alice@mergington.edu"
        email_upper = "ALICE@MERGINGTON.EDU"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup/{email_upper}"
        )

        # Assert
        assert response.status_code == 200
        assert email_lower not in fresh_activities[activity_name]["participants"]

    def test_remove_multiple_participants_from_full_activity(self, client, fresh_activities):
        """
        Arrange: Gym Class is full (2/2)
        Act: Remove one participant and add a new one
        Assert: Verify capacity constraint is properly applied after removal
        """
        # Arrange
        activity_name = "Gym Class"
        to_remove = "john@mergington.edu"
        to_add = "charlie@mergington.edu"

        # Act - Remove John
        response1 = client.delete(
            f"/activities/{activity_name}/signup/{to_remove}"
        )

        # Act - Add Charlie (should succeed now that there's space)
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": to_add}
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert to_remove not in fresh_activities[activity_name]["participants"]
        assert to_add in fresh_activities[activity_name]["participants"]


class TestRootEndpoint:
    """Tests for GET / endpoint."""

    def test_root_redirects_to_index(self, client):
        """
        Arrange: Request root endpoint
        Act: Make request to /
        Assert: Verify redirect to /static/index.html
        """
        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
