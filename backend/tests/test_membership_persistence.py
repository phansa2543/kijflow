import uuid

import pytest
from sqlalchemy import insert, delete
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.models.organization import Organization
from app.models.membership import Membership

def test_reject_invalid_membership_profile(db_connection):
    user_id = uuid.uuid4()
    organization_id = uuid.uuid4()
    membership_id = uuid.uuid4()

    db_connection.execute(
        insert(User).values(
            id=user_id,
        )
    )

    db_connection.execute(
        insert(Organization).values(
            id=organization_id,
            name="Test Organization",
        )
    )

    with pytest.raises(IntegrityError):
        db_connection.execute(
            insert(Membership).values(
                id=membership_id,
                user_id=user_id,
                organization_id=organization_id,
                profile="INVALID",
                status="ACTIVE",
            )
        )

def test_rejects_invalid_membership_status(db_connection):
    user_id = uuid.uuid4()
    organization_id = uuid.uuid4()
    membership_id = uuid.uuid4()

    db_connection.execute(
        insert(User).values(
            id=user_id,
        )
    )

    db_connection.execute(
        insert(Organization).values(
            id=organization_id,
            name="Test Organization",
        )
    )

    with pytest.raises(IntegrityError):
        db_connection.execute(
            insert(Membership).values(
                id=membership_id,
                user_id=user_id,
                organization_id=organization_id,
                profile="MEMBER",
                status="INVALID",
            )
        )

def test_rejects_non_active_owner(db_connection):
    user_id = uuid.uuid4()
    organization_id = uuid.uuid4()
    membership_id = uuid.uuid4()

    db_connection.execute(
        insert(User).values(
            id=user_id,
        )
    )

    db_connection.execute(
        insert(Organization).values(
            id=organization_id,
            name="Test Organization",
        )
    )

    with pytest.raises(IntegrityError):
        db_connection.execute(
            insert(Membership).values(
                id=membership_id,
                user_id=user_id,
                organization_id=organization_id,
                profile="OWNER",
                status="DISABLED",
            )
        )

def test_rejects_duplicate_user_organization_membership(db_connection):
    user_id = uuid.uuid4()
    organization_id = uuid.uuid4()

    db_connection.execute(
        insert(User).values(
            id=user_id,
        )
    )

    db_connection.execute(
        insert(Organization).values(
            id=organization_id,
            name="Test Organization",
        )
    )

    db_connection.execute(
        insert(Membership).values(
            id=uuid.uuid4(),
            user_id=user_id,
            organization_id=organization_id,
            profile="MEMBER",
            status="ACTIVE",
        )
    )

    with pytest.raises(IntegrityError):
        db_connection.execute(
            insert(Membership).values(
                id=uuid.uuid4(),
                user_id=user_id,
                organization_id=organization_id,
                profile="ADMIN",
                status="ACTIVE",
            )
        )

def test_rejects_second_owner_in_same_organization(db_connection):
    first_user_id = uuid.uuid4()
    second_user_id = uuid.uuid4()
    organization_id = uuid.uuid4()

    db_connection.execute(
        insert(User).values(id=first_user_id)
    )

    db_connection.execute(
        insert(User).values(id=second_user_id)
    )

    db_connection.execute(
        insert(Organization).values(
            id=organization_id,
            name="Test Organization",
        )
    )

    db_connection.execute(
        insert(Membership).values(
            id=uuid.uuid4(),
            user_id=first_user_id,
            organization_id=organization_id,
            profile="OWNER",
            status="ACTIVE",
        )
    )

    with pytest.raises(IntegrityError):
        db_connection.execute(
            insert(Membership).values(
                id=uuid.uuid4(),
                user_id=second_user_id,
                organization_id=organization_id,
                profile="OWNER",
                status="ACTIVE",
            )
        )

def test_allows_multiple_membership_in_same_organization(db_connection):
    first_user_id = uuid.uuid4()
    second_user_id = uuid.uuid4()
    organization_id = uuid.uuid4()

    db_connection.execute(
        insert(User).values(id=first_user_id)
    )

    db_connection.execute(
        insert(User).values(id=second_user_id)
    )

    db_connection.execute(
        insert(Organization).values(
            id=organization_id,
            name="Test Organization",
        )
    )

    db_connection.execute(
        insert(Membership).values(
            id=uuid.uuid4(),
            user_id=first_user_id,
            organization_id=organization_id,
            profile="MEMBER",
            status="ACTIVE",
        )
    )

    db_connection.execute(
        insert(Membership).values(
            id=uuid.uuid4(),
            user_id=second_user_id,
            organization_id=organization_id,
            profile="MEMBER",
            status="ACTIVE",
        )
    )

def test_allows_user_membership_in_multiple_organizations(db_connection):
    user_id = uuid.uuid4()
    first_organization_id = uuid.uuid4()
    second_organization_id = uuid.uuid4()

    db_connection.execute(
        insert(User).values(id=user_id)
    )

    db_connection.execute(
        insert(Organization).values(
            id=first_organization_id,
            name="Organization A",
        )
    )

    db_connection.execute(
        insert(Organization).values(
            id=second_organization_id,
            name="Organization B",
        )
    )

    db_connection.execute(
        insert(Membership).values(
            id=uuid.uuid4(),
            user_id=user_id,
            organization_id=first_organization_id,
            profile="MEMBER",
            status="ACTIVE",
        )
    )

    db_connection.execute(
        insert(Membership).values(
            id=uuid.uuid4(),
            user_id=user_id,
            organization_id=second_organization_id,
            profile="MEMBER",
            status="ACTIVE",
        )
    )

def test_allows_disabled_member(db_connection):
    user_id = uuid.uuid4()
    organization_id = uuid.uuid4()

    db_connection.execute(
        insert(User).values(id=user_id)
    )

    db_connection.execute(
        insert(Organization).values(
            id=organization_id,
            name="Test Organization",
        )
    )

    db_connection.execute(
        insert(Membership).values(
            id=uuid.uuid4(),
            user_id=user_id,
            organization_id=organization_id,
            profile="MEMBER",
            status="DISABLED",
        )
    )

def test_allows_revoked_member(db_connection):
    user_id = uuid.uuid4()
    organization_id = uuid.uuid4()

    db_connection.execute(
        insert(User).values(id=user_id)
    )

    db_connection.execute(
        insert(Organization).values(
            id=organization_id,
            name="Test Organization",
        )
    )

    db_connection.execute(
        insert(Membership).values(
            id=uuid.uuid4(),
            user_id=user_id,
            organization_id=organization_id,
            profile="MEMBER",
            status="REVOKED",
        )
    )

def test_rejects_deleting_user_with_membership(db_connection):
    user_id = uuid.uuid4()
    organization_id = uuid.uuid4()

    db_connection.execute(
        insert(User).values(id=user_id)
    )

    db_connection.execute(
        insert(Organization).values(
            id=organization_id,
            name="Test Organization",
        )
    )

    db_connection.execute(
        insert(Membership).values(
            id=uuid.uuid4(),
            user_id=user_id,
            organization_id=organization_id,
            profile="MEMBER",
            status="ACTIVE",
        )
    )

    with pytest.raises(IntegrityError):
        db_connection.execute(
            delete(User).where(User.id == user_id)
        )

def test_rejects_deleting_organization_with_membership(db_connection):
    user_id = uuid.uuid4()
    organization_id = uuid.uuid4()

    db_connection.execute(
        insert(User).values(id=user_id)
    )

    db_connection.execute(
        insert(Organization).values(
            id=organization_id,
            name="Test Organization",
        )
    )

    db_connection.execute(
        insert(Membership).values(
            id=uuid.uuid4(),
            user_id=user_id,
            organization_id=organization_id,
            profile="MEMBER",
            status="ACTIVE",
        )
    )

    with pytest.raises(IntegrityError):
        db_connection.execute(
            delete(Organization).where(
                Organization.id == organization_id
            )
        )

def test_rejects_blank_organization_name(db_connection):
    with pytest.raises(IntegrityError):
        db_connection.execute(
            insert(Organization).values(
                id=uuid.uuid4(),
                name="   "
,            )
        )

def test_rejects_duplicate_membership_after_revocation(db_connection):
    user_id = uuid.uuid4()
    organization_id = uuid.uuid4()

    db_connection.execute(
        insert(User).values(id=user_id)
    )

    db_connection.execute(
        insert(Organization).values(
            id=organization_id,
            name="Test Organization",
        )
    )

    db_connection.execute(
        insert(Membership).values(
            id=uuid.uuid4(),
            user_id=user_id,
            organization_id=organization_id,
            profile="MEMBER",
            status="REVOKED",
        )
    )

    with pytest.raises(IntegrityError):
        db_connection.execute(
            insert(Membership).values(
                id=uuid.uuid4(),
                user_id=user_id,
                organization_id=organization_id,
                profile="MEMBER",
                status="ACTIVE",
            )
        )

def test_allows_organization_without_owner(db_connection):
    db_connection.execute(
        insert(Organization).values(
            id=uuid.uuid4(),
            name="Raw Organization",
        )
    )

def test_allows_user_without_membership(db_connection):
    db_connection.execute(
        insert(User).values(
            id=uuid.uuid4(),
        )
    )