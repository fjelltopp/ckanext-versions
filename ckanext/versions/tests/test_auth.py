import pytest
from ckan import model
from ckan.plugins import toolkit
from ckan.tests import factories, helpers


@pytest.fixture
def org_admin():
    return factories.User()


@pytest.fixture
def org_editor():
    return factories.User()


@pytest.fixture
def org_member():
    return factories.User()


@pytest.fixture
def other_org_admin():
    return factories.User()


@pytest.fixture
def admin_user():
    return factories.Sysadmin()


@pytest.fixture
def org(org_admin, org_editor, org_member):
    return factories.Organization(
        users=[
            {'name': org_admin['name'], 'capacity': 'admin'},
            {'name': org_editor['name'], 'capacity': 'editor'},
            {'name': org_member['name'], 'capacity': 'member'},
        ]
    )


@pytest.fixture
def other_org(other_org_admin):
    return factories.Organization(
        users=[
            {'name': other_org_admin['name'], 'capacity': 'admin'},
        ]
    )


@pytest.fixture
def private_dataset(org):
    return factories.Dataset(owner_org=org['id'], private=True)


@pytest.fixture
def public_dataset(org):
    return factories.Dataset(owner_org=org['id'], private=False)


@pytest.mark.usefixtures("clean_db_with_migrations", "versions_setup", "with_plugins")
class TestVersionsAuth(object):

    def _get_context(self, user):
        return {
            'model': model,
            'user': user if isinstance(user, str) else user['name']
        }

    @pytest.mark.parametrize("user_type, dataset_type", [
        ('org_admin', 'private_dataset'),
        ('org_admin', 'public_dataset'),
        ('org_editor', 'private_dataset'),
        ('org_editor', 'public_dataset'),
        ('admin_user', 'private_dataset'),
        ('admin_user', 'public_dataset'),
    ])
    def test_create_is_authorized(self, user_type, dataset_type, request):
        """Test that authorized users can create versions on a given dataset
        """
        user = request.getfixturevalue(user_type)
        dataset = request.getfixturevalue(dataset_type)
        context = self._get_context(user)
        assert helpers.call_auth('version_create',
                                 context=context,
                                 package_id=dataset['id'])

    @pytest.mark.parametrize("user_type, dataset_type", [
        ('org_member', 'private_dataset'),
        ('org_member', 'public_dataset'),
        ('other_org_admin', 'private_dataset'),
        ('other_org_admin', 'public_dataset'),
    ])
    def test_create_is_unauthorized(self, user_type, dataset_type, request):
        """Test that unauthorized users cannot create versions on a given
        dataset
        """
        user = request.getfixturevalue(user_type)
        dataset = request.getfixturevalue(dataset_type)
        context = self._get_context(user)
        with pytest.raises(toolkit.NotAuthorized):
            helpers.call_auth(
                'version_create',
                context=context,
                package_id=dataset['id'])

    @pytest.mark.parametrize("user_type, dataset_type", [
        ('org_admin', 'private_dataset'),
        ('org_admin', 'public_dataset'),
        ('org_editor', 'private_dataset'),
        ('org_editor', 'public_dataset'),
        ('admin_user', 'private_dataset'),
        ('admin_user', 'public_dataset'),
    ])
    def test_delete_is_authorized(self, user_type, dataset_type, request):
        """Test that authorized users can delete versions on a given dataset
        """
        user = request.getfixturevalue(user_type)
        dataset = request.getfixturevalue(dataset_type)
        context = self._get_context(user)
        assert helpers.call_auth('version_delete',
                                 context=context,
                                 package_id=dataset['id'])

    @pytest.mark.parametrize("user_type, dataset_type", [
        ('org_member', 'private_dataset'),
        ('org_member', 'public_dataset'),
        ('other_org_admin', 'private_dataset'),
        ('other_org_admin', 'public_dataset'),
    ])
    def test_delete_is_unauthorized(self, user_type, dataset_type, request):
        """Test that unauthorized users cannot delete versions on a given
        dataset
        """
        user = request.getfixturevalue(user_type)
        dataset = request.getfixturevalue(dataset_type)
        context = self._get_context(user)
        with pytest.raises(toolkit.NotAuthorized):
            helpers.call_auth(
                'version_delete',
                context=context,
                package_id=dataset['id'])

    @pytest.mark.parametrize("user_type, dataset_type", [
        ('org_admin', 'private_dataset'),
        ('org_admin', 'public_dataset'),
        ('org_editor', 'private_dataset'),
        ('org_editor', 'public_dataset'),
        ('org_member', 'private_dataset'),
        ('org_member', 'public_dataset'),
        ('admin_user', 'private_dataset'),
        ('admin_user', 'public_dataset'),
        ('other_org_admin', 'public_dataset'),
    ])
    def test_list_is_authorized(self, user_type, dataset_type, request):
        """Test that authorized users can list versions of a given dataset
        """
        user = request.getfixturevalue(user_type)
        dataset = request.getfixturevalue(dataset_type)
        context = self._get_context(user)
        assert helpers.call_auth('version_list',
                                 context=context,
                                 package_id=dataset['id'])

    @pytest.mark.parametrize("user_type, dataset_type", [
        ('other_org_admin', 'private_dataset'),
    ])
    def test_list_is_unauthorized(self, user_type, dataset_type, request):
        """Test that unauthorized users cannot list versions on a given
        dataset
        """
        user = request.getfixturevalue(user_type)
        dataset = request.getfixturevalue(dataset_type)
        context = self._get_context(user)
        with pytest.raises(toolkit.NotAuthorized):
            helpers.call_auth(
                'version_list',
                context=context,
                package_id=dataset['id'])

    @pytest.mark.parametrize("user_type, dataset_type", [
        ('org_admin', 'private_dataset'),
        ('org_admin', 'public_dataset'),
        ('org_editor', 'private_dataset'),
        ('org_editor', 'public_dataset'),
        ('org_member', 'private_dataset'),
        ('org_member', 'public_dataset'),
        ('admin_user', 'private_dataset'),
        ('admin_user', 'public_dataset'),
        ('other_org_admin', 'public_dataset'),
    ])
    def test_show_is_authorized(self, user_type, dataset_type, request):
        """Test that authorized users can view versions of a given dataset
        """
        user = request.getfixturevalue(user_type)
        dataset = request.getfixturevalue(dataset_type)
        context = self._get_context(user)
        assert helpers.call_auth('version_show',
                                 context=context,
                                 package_id=dataset['id'])

    @pytest.mark.parametrize("user_type, dataset_type", [
        ('other_org_admin', 'private_dataset'),
    ])
    def test_show_is_unauthorized(self, user_type, dataset_type, request):
        """Test that unauthorized users cannot view versions on a given
        dataset
        """
        user = request.getfixturevalue(user_type)
        dataset = request.getfixturevalue(dataset_type)
        context = self._get_context(user)
        with pytest.raises(toolkit.NotAuthorized):
            helpers.call_auth(
                'version_show',
                context=context,
                package_id=dataset['id'])
