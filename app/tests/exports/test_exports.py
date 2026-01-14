from django.test import TestCase
from django.contrib.auth.models import User
from exports.models import Export
from species.models import Species
from locations.models import Location
from observations.models import Observation
from unittest.mock import patch, MagicMock
from middleware.current_user import _user


class ExportZipFileTestCase(TestCase):
    """Test case for export zip file functionality"""

    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        _user.value = self.user

        # Create test species
        self.species = Species.objects.create(
            scientific_name='Test Species',
            common_name='Test'
        )

        # Create test location
        self.location = Location.objects.create(
            name='Test Location',
            latitude=60.1699,
            longitude=24.9384
        )

        # Create test observation
        self.observation = Observation.objects.create(
            species=self.species,
            location=self.location,
            observer=self.user,
            observation_date='2024-01-01'
        )

        # Create test export
        self.export = Export.objects.create(
            user=self.user,
            status='pending'
        )

    @patch('exports.views.search_wdpa')
    def test_export_creation(self, mock_search_wdpa):
        """Test export creation"""
        mock_search_wdpa.return_value = MagicMock()
        
        self.assertIsNotNone(self.export)
        self.assertEqual(self.export.status, 'pending')
        self.assertEqual(self.export.user, self.user)

    @patch('exports.views.search_wdpa')
    def test_export_includes_observations(self, mock_search_wdpa):
        """Test that export includes observations"""
        mock_search_wdpa.return_value = MagicMock()
        
        # Add observation to export
        self.export.observations.add(self.observation)
        
        self.assertEqual(self.export.observations.count(), 1)
        self.assertIn(self.observation, self.export.observations.all())

    @patch('exports.views.search_wdpa')
    def test_export_status_updates(self, mock_search_wdpa):
        """Test export status updates"""
        mock_search_wdpa.return_value = MagicMock()
        
        self.export.status = 'completed'
        self.export.save()
        
        updated_export = Export.objects.get(id=self.export.id)
        self.assertEqual(updated_export.status, 'completed')

    def test_export_user_relationship(self):
        """Test export user relationship"""
        self.assertEqual(self.export.user, self.user)
        self.assertIn(self.export, self.user.export_set.all())

    @patch('exports.views.search_wdpa')
    def test_export_file_generation(self, mock_search_wdpa):
        """Test export file generation"""
        mock_search_wdpa.return_value = MagicMock()
        
        # Test that export can be associated with a file
        self.export.file = 'exports/test_export.zip'
        self.export.save()
        
        updated_export = Export.objects.get(id=self.export.id)
        self.assertEqual(updated_export.file, 'exports/test_export.zip')

    @patch('exports.views.search_wdpa')
    def test_export_multiple_observations(self, mock_search_wdpa):
        """Test export with multiple observations"""
        mock_search_wdpa.return_value = MagicMock()
        
        # Create additional observations
        obs2 = Observation.objects.create(
            species=self.species,
            location=self.location,
            observer=self.user,
            observation_date='2024-01-02'
        )
        
        obs3 = Observation.objects.create(
            species=self.species,
            location=self.location,
            observer=self.user,
            observation_date='2024-01-03'
        )
        
        # Add observations to export
        self.export.observations.add(self.observation, obs2, obs3)
        
        self.assertEqual(self.export.observations.count(), 3)

    @patch('exports.views.search_wdpa')
    def test_export_deletion(self, mock_search_wdpa):
        """Test export deletion"""
        mock_search_wdpa.return_value = MagicMock()
        
        export_id = self.export.id
        self.export.delete()
        
        with self.assertRaises(Export.DoesNotExist):
            Export.objects.get(id=export_id)

    def test_export_string_representation(self):
        """Test export string representation"""
        expected_str = f"Export {self.export.id} - {self.export.status}"
        self.assertEqual(str(self.export), expected_str)

    @patch('exports.views.search_wdpa')
    def test_export_ordering(self, mock_search_wdpa):
        """Test export ordering"""
        mock_search_wdpa.return_value = MagicMock()
        
        # Create multiple exports
        export2 = Export.objects.create(
            user=self.user,
            status='completed'
        )
        
        export3 = Export.objects.create(
            user=self.user,
            status='failed'
        )
        
        exports = Export.objects.all().order_by('-created_at')
        self.assertEqual(exports[0], export3)
        self.assertEqual(exports[1], export2)
        self.assertEqual(exports[2], self.export)


class ExportFilterTestCase(TestCase):
    """Test case for export filtering functionality"""

    def setUp(self):
        """Set up test data"""
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1',
            password='testpass1'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            password='testpass2'
        )
        _user.value = self.user1

        # Create exports for different users
        self.export1 = Export.objects.create(
            user=self.user1,
            status='pending'
        )
        self.export2 = Export.objects.create(
            user=self.user1,
            status='completed'
        )
        self.export3 = Export.objects.create(
            user=self.user2,
            status='pending'
        )

    def test_filter_by_user(self):
        """Test filtering exports by user"""
        user1_exports = Export.objects.filter(user=self.user1)
        self.assertEqual(user1_exports.count(), 2)
        self.assertIn(self.export1, user1_exports)
        self.assertIn(self.export2, user1_exports)
        self.assertNotIn(self.export3, user1_exports)

    def test_filter_by_status(self):
        """Test filtering exports by status"""
        pending_exports = Export.objects.filter(status='pending')
        self.assertEqual(pending_exports.count(), 2)
        self.assertIn(self.export1, pending_exports)
        self.assertNotIn(self.export2, pending_exports)

    def test_filter_by_user_and_status(self):
        """Test filtering exports by user and status"""
        user1_pending = Export.objects.filter(user=self.user1, status='pending')
        self.assertEqual(user1_pending.count(), 1)
        self.assertEqual(user1_pending.first(), self.export1)


class ExportAuditFieldsTestCase(TestCase):
    """Test case for export audit fields (created_at, updated_at)"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        _user.value = self.user
        
        self.export = Export.objects.create(
            user=self.user,
            status='pending'
        )

    def test_created_at_auto_set(self):
        """Test that created_at is automatically set"""
        self.assertIsNotNone(self.export.created_at)

    def test_updated_at_auto_set(self):
        """Test that updated_at is automatically set"""
        self.assertIsNotNone(self.export.updated_at)

    def test_updated_at_changes_on_save(self):
        """Test that updated_at changes when object is saved"""
        original_updated_at = self.export.updated_at
        
        # Update export
        self.export.status = 'completed'
        self.export.save()
        
        self.assertNotEqual(self.export.updated_at, original_updated_at)
        self.assertGreater(self.export.updated_at, original_updated_at)

    def test_created_at_does_not_change(self):
        """Test that created_at does not change on save"""
        original_created_at = self.export.created_at
        
        # Update export
        self.export.status = 'completed'
        self.export.save()
        
        self.assertEqual(self.export.created_at, original_created_at)
