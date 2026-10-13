import unittest
import logging
from unittest.mock import patch
from services.ActivityService import ActivityService
from repository.Repository_activity import MemoryRepository
from domain.Activity import Activity

class TestActivityService(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.patcher = patch('services.ActivityService.ActivityService.ensure_activity_date')
        self.mock_ensure_data = self.patcher.start()

        self.repo = MemoryRepository()
        self.service = ActivityService(self.repo)
        logging.info("Set up for ActivityService tests completed.")

    def tearDown(self):
        self.patcher.stop()
        logging.info("Tore down ActivityService tests.")

    def test_add_activity(self):
        logging.info("Running test_add_activity...")
        self.service.add_activity(1, [1, 2], "2024/01/01", "12:00", "Test Activity")
        self.assertEqual(len(self.service.get_all_service()), 1)
        self.assertEqual(self.service.get_all_service()[0].description, "Test Activity")
        logging.info("test_add_activity finished.")

    def test_remove_activity(self):
        logging.info("Running test_remove_activity...")
        self.service.add_activity(1, [1, 2], "2024/01/01", "12:00", "Test Activity")
        self.service.remove_activity(1)
        self.assertEqual(len(self.service.get_all_service()), 0)
        logging.info("test_remove_activity finished.")

    def test_update_activity(self):
        logging.info("Running test_update_activity...")
        self.service.add_activity(1, [1, 2], "2024-01-01", "12:00", "Test Activity")
        self.service.update_activity(1, [3, 4], "2025-02-02", "14:00", "Updated Activity")
        activity = self.service.get_all_service()[0]
        self.assertEqual(activity.person_id, [3, 4])
        self.assertEqual(activity.date, "2025-02-02")
        self.assertEqual(activity.time, "14:00")
        self.assertEqual(activity.description, "Updated Activity")
        logging.info("test_update_activity finished.")

    def test_search_activity(self):
        logging.info("Running test_search_activity...")
        self.service.add_activity(1, [1, 2], "2024-01-01", "12:00", "Swimming")
        self.service.add_activity(2, [3, 4], "2024-01-02", "14:00", "Running")
        results = self.service.search_activity("Swim")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].description, "Swimming")
        logging.info("test_search_activity finished.")

if __name__ == '__main__':
    unittest.main()
