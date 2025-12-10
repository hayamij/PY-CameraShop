"""
Integration tests for UserRepository
Tests the repository against a real database
"""
import pytest
from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.enums import UserRole
from app.domain.exceptions import UserNotFoundException, UserAlreadyExistsException
from app.adapters.repositories.user_repository_adapter import UserRepositoryAdapter


class TestUserRepositoryIntegration:
    """Integration tests for UserRepository"""

    def test_save_creates_user_in_database(self, user_repository, db_session):
        """Test that save() creates a user in the database"""
        # Arrange
        user = User(
            username="testuser123",
            email=Email("testuser123@example.com"),
            password_hash="hashed_password_123",
            full_name="Test User",
            role=UserRole.CUSTOMER
        )

        # Act
        saved_user = user_repository.save(user)

        # Assert
        assert saved_user.id is not None
        assert saved_user.username == "testuser123"
        assert saved_user.email.address == "testuser123@example.com"
        assert saved_user.full_name == "Test User"
        assert saved_user.role == UserRole.CUSTOMER

    def test_find_by_id_retrieves_correct_user(self, user_repository, sample_user):
        """Test that find_by_id() retrieves the correct user"""
        # Act
        found_user = user_repository.find_by_id(sample_user.id)

        # Assert
        assert found_user is not None
        assert found_user.id == sample_user.id
        assert found_user.username == sample_user.username
        assert found_user.email.address == sample_user.email.address

    def test_find_by_username_retrieves_correct_user(self, user_repository, sample_user):
        """Test that find_by_username() retrieves the correct user"""
        # Act
        found_user = user_repository.find_by_username(sample_user.username)

        # Assert
        assert found_user is not None
        assert found_user.username == sample_user.username
        assert found_user.email.address == sample_user.email.address

    def test_find_by_email_retrieves_correct_user(self, user_repository, sample_user):
        """Test that find_by_email() retrieves the correct user"""
        # Act
        found_user = user_repository.find_by_email(sample_user.email)

        # Assert
        assert found_user is not None
        assert found_user.email.address == sample_user.email.address
        assert found_user.username == sample_user.username

    def test_find_by_id_returns_none_when_not_found(self, user_repository):
        """Test that find_by_id() returns None when user doesn't exist"""
        # Act
        result = user_repository.find_by_id(99999)
        
        # Assert
        assert result is None

    def test_find_by_username_returns_none_when_not_found(self, user_repository):
        """Test that find_by_username() returns None when user doesn't exist"""
        # Act
        result = user_repository.find_by_username("nonexistent_user")

        # Assert
        assert result is None

    def test_save_raises_exception_on_duplicate_username(self, user_repository, sample_user):
        """Test that save() raises UserAlreadyExistsException on duplicate username"""
        # Arrange
        duplicate_user = User(
            username=sample_user.username,  # Same username
            email=Email("different@example.com"),
            password_hash="hashed_password",
            full_name="Different User",
            role=UserRole.CUSTOMER
        )

        # Act & Assert
        with pytest.raises(UserAlreadyExistsException) as exc_info:
            user_repository.save(duplicate_user)
        
        assert "username" in str(exc_info.value).lower() and "already exists" in str(exc_info.value).lower()

    def test_save_raises_exception_on_duplicate_email(self, user_repository, sample_user):
        """Test that save() raises UserAlreadyExistsException on duplicate email"""
        # Arrange
        duplicate_user = User(
            username="different_username",
            email=sample_user.email,  # Same email
            password_hash="hashed_password",
            full_name="Different User",
            role=UserRole.CUSTOMER
        )

        # Act & Assert
        with pytest.raises(UserAlreadyExistsException) as exc_info:
            user_repository.save(duplicate_user)
        
        assert "email" in str(exc_info.value).lower() and "already exists" in str(exc_info.value).lower()

    def test_update_user_successfully(self, user_repository, sample_user):
        """Test that update() updates user information"""
        # Arrange
        sample_user.update_profile(full_name="Updated Name")

        # Act
        updated_user = user_repository.save(sample_user)

        # Assert
        assert updated_user.full_name == "Updated Name"
        
        # Verify it persisted
        found_user = user_repository.find_by_id(sample_user.id)
        assert found_user.full_name == "Updated Name"

    def test_user_count_increases_after_save(self, user_repository, db_session):
        """Test that user count increases after saving a new user"""
        # Arrange
        from app.infrastructure.database.models import UserModel
        initial_count = db_session.query(UserModel).count()

        user = User(
            username="newuser456",
            email=Email("newuser456@example.com"),
            password_hash="hashed_password",
            full_name="New User",
            role=UserRole.CUSTOMER
        )

        # Act
        user_repository.save(user)
        
        # Assert
        new_count = db_session.query(UserModel).count()
        assert new_count == initial_count + 1

    def test_entity_to_model_conversion_preserves_data(self, user_repository):
        """Test that entity to model conversion preserves all data correctly"""
        # Arrange
        user = User(
            username="conversiontest",
            email=Email("conversion@test.com"),
            password_hash="hashed_pwd",
            full_name="Conversion Test",
            role=UserRole.ADMIN
        )

        # Act
        saved_user = user_repository.save(user)
        retrieved_user = user_repository.find_by_id(saved_user.id)

        # Assert - All fields should match
        assert retrieved_user.username == user.username
        assert retrieved_user.email.address == user.email.address
        assert retrieved_user.password_hash == user.password_hash
        assert retrieved_user.full_name == user.full_name
        assert retrieved_user.role == user.role
