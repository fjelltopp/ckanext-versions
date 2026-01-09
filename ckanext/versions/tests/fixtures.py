import pytest

from ckan import model
from ckan.tests import factories
from ckanext.versions.tests import create_version, versions_db_setup


@pytest.fixture
def versions_setup():
    versions_db_setup()


@pytest.fixture
def clean_db_with_migrations(clean_db):
    """
    Extends clean_db fixture to add CKAN 2.11 activity plugin schema.

    The activity plugin in CKAN 2.11 requires a permission_labels column
    in the activity table. This fixture ensures the column exists after
    clean_db resets the database.
    """
    # After clean_db runs, add the permission_labels column
    connection = model.Session.connection()
    connection.execute(
        "ALTER TABLE activity ADD COLUMN IF NOT EXISTS permission_labels text[];"
    )
    model.Session.commit()


@pytest.fixture()
def org_admin():
    return factories.User(name="admin")


@pytest.fixture()
def org_editor():
    return factories.User(name="editor")


@pytest.fixture()
def org_member():
    return factories.User(name="member")


@pytest.fixture()
def test_organization(org_admin, org_editor, org_member):
    return factories.Organization(users=[
        {'name': org_admin['id'], 'capacity': 'admin'},
        {'name': org_editor['id'], 'capacity': 'editor'},
        {'name': org_member['id'], 'capacity': 'member'}
    ])


@pytest.fixture()
def test_dataset(test_organization):
    return factories.Dataset(owner_org=test_organization['id'])


@pytest.fixture()
def test_resource(test_dataset):
    return factories.Resource(package_id=test_dataset['id'])


@pytest.fixture()
def test_version(test_dataset, org_editor):
    return create_version(test_dataset['id'], org_editor, version_name="Version1")
