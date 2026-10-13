"""
Tests for the undo/redo functionality (Command pattern).

Covers:
1. Undo/redo for add, remove and update operations
2. Cascading deletion (removing a person from activities) and its restoration
3. Several undo/redo steps in a row
4. Clearing the redo stack after a new operation
"""

import unittest
from unittest.mock import patch

from repository.Repository_person import MemoryRepository as PersonMemoryRepo
from repository.Repository_activity import MemoryRepository as ActivityMemoryRepo
from services.PersonService import PersonService
from services.ActivityService import ActivityService
from UndoRedoService import UndoRedoService


class TestUndoRedo(unittest.TestCase):

    def setUp(self):
        # Start every test with empty repositories (no generated fake data)
        self.patchers = [
            patch("services.ActivityService.ActivityService.ensure_activity_date"),
            patch("services.PersonService.PersonService.ensure_person_data"),
        ]
        for p in self.patchers:
            p.start()

        self.undo_redo = UndoRedoService()
        self.activity_service = ActivityService(ActivityMemoryRepo(), self.undo_redo)
        self.person_service = PersonService(PersonMemoryRepo(), self.activity_service, self.undo_redo)

    def tearDown(self):
        for p in self.patchers:
            p.stop()

    def count_persons(self):
        return len(self.person_service.get_all_service())

    def test_add_undo_redo(self):
        self.person_service.add_person_from_string("John Doe", "1234567890")
        self.assertEqual(self.count_persons(), 1)

        self.undo_redo.undo()
        self.assertEqual(self.count_persons(), 0)

        self.undo_redo.redo()
        self.assertEqual(self.count_persons(), 1)

    def test_cascading_delete_undo(self):
        self.person_service.add_person(1, "Alice", "1111111111")
        self.person_service.add_person(2, "Bob", "2222222222")
        self.person_service.add_person(3, "Charlie", "3333333333")
        self.activity_service.add_activity(1, [1, 2, 3], "2025-01-15", "10:00", "Team Meeting")

        self.person_service.remove_person("Alice")
        person_ids = [p.person_id for p in self.person_service.get_all_service()]
        self.assertNotIn(1, person_ids)
        self.assertNotIn(1, self.activity_service.get_all_service()[0].person_id)

        self.undo_redo.undo()
        person_ids = [p.person_id for p in self.person_service.get_all_service()]
        self.assertIn(1, person_ids)
        self.assertIn(1, self.activity_service.get_all_service()[0].person_id)

    def test_update_undo_redo(self):
        self.person_service.add_person(1, "Original Name", "1234567890")

        self.person_service.update_person(1, "Updated Name", "9876543210")
        person = self.person_service.get_by_id(1)
        self.assertEqual((person.name, person.phone_number), ("Updated Name", "9876543210"))

        self.undo_redo.undo()
        person = self.person_service.get_by_id(1)
        self.assertEqual((person.name, person.phone_number), ("Original Name", "1234567890"))

        self.undo_redo.redo()
        person = self.person_service.get_by_id(1)
        self.assertEqual((person.name, person.phone_number), ("Updated Name", "9876543210"))

    def test_multiple_undo_redo(self):
        self.person_service.add_person_from_string("Person 1", "1111111111")
        self.person_service.add_person_from_string("Person 2", "2222222222")
        self.person_service.add_person_from_string("Person 3", "3333333333")

        for expected in (2, 1, 0):
            self.undo_redo.undo()
            self.assertEqual(self.count_persons(), expected)

        for expected in (1, 2, 3):
            self.undo_redo.redo()
            self.assertEqual(self.count_persons(), expected)

    def test_redo_stack_cleared_after_new_operation(self):
        self.person_service.add_person_from_string("Person 1", "1111111111")
        self.undo_redo.undo()
        self.assertTrue(self.undo_redo.can_redo())

        self.person_service.add_person_from_string("Person 2", "2222222222")
        self.assertFalse(self.undo_redo.can_redo())

    def test_undo_with_empty_history_raises(self):
        with self.assertRaises(IndexError):
            self.undo_redo.undo()

    def test_activity_add_undo_redo(self):
        self.person_service.add_person(1, "Person 1", "1111111111")
        self.person_service.add_person(2, "Person 2", "2222222222")

        self.activity_service.add_activity_with_undo([1, 2], "2025-01-15", "10:00", "Meeting")
        self.assertEqual(len(self.activity_service.get_all_service()), 1)

        self.undo_redo.undo()
        self.assertEqual(len(self.activity_service.get_all_service()), 0)

        self.undo_redo.redo()
        self.assertEqual(len(self.activity_service.get_all_service()), 1)


if __name__ == "__main__":
    unittest.main()
