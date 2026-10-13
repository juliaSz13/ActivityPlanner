import unittest
import logging
from unittest.mock import patch, MagicMock
from services.PersonService import PersonService
from repository.Repository_person import MemoryRepository


class TestPersonService(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.patcher_ensure_data = patch('services.PersonService.PersonService.ensure_person_data')
        self.mock_ensure_data = self.patcher_ensure_data.start()

        self.mock_activity_service = MagicMock()

        self.repo = MemoryRepository()
        self.service = PersonService(self.repo, self.mock_activity_service)

        logging.info("Set up for PersonService tests completed.")

    def tearDown(self):
        self.patcher_ensure_data.stop()
        logging.info("Tore down PersonService tests.")

    def test_add_person(self):
        logging.info("Running test_add_person...")
        self.service.add_person(1, "John Doe", "1234567890")
        self.assertEqual(len(self.service.get_all_service()), 1)
        self.assertEqual(self.service.get_all_service()[0].name, "John Doe")
        logging.info("test_add_person finished.")

    def test_remove_person_by_name(self):
        logging.info("Running test_remove_person_by_name...")
        self.service.add_person(1, "John Doe", "1234567890")
        self.service.add_person(2, "Jane Smith", "1112223334")
        self.service.remove_person("John Doe")

        self.assertEqual(len(self.service.get_all_service()), 1)
        self.assertEqual(self.service.get_all_service()[0].name, "Jane Smith")

        logging.info("test_remove_person_by_name finished.")

    def test_update_person(self):
        logging.info("Running test_update_person...")
        self.service.add_person(1, "John Doe", "1234567890")
        self.service.update_person(1, "Jane Doe", "0987654321")

        person = self.service.get_by_id(1)
        self.assertEqual(person.name, "Jane Doe")
        self.assertEqual(person.phone_number, "0987654321")

        logging.info("test_update_person finished.")

    def test_search_person(self):
        logging.info("Running test_search_person...")
        self.service.add_person(1, "John Doe", "1234567890")
        self.service.add_person(2, "Jane Smith", "0987654321")

        results_name = self.service.search_person("Doe")
        self.assertEqual(len(results_name), 1)
        self.assertEqual(results_name[0].name, "John Doe")

        results_phone = self.service.search_person("0987")
        self.assertEqual(len(results_phone), 1)
        self.assertEqual(results_phone[0].name, "Jane Smith")

        logging.info("test_search_person finished.")


if __name__ == '__main__':
    unittest.main()