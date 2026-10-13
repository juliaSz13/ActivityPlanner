
from services.PersonService import (PersonService)
from services.ActivityService import ActivityService
from services.ActivityService import ActivityException
from services.PersonService import PersonException
from UndoRedoService import UndoRedoService


class UI:
    """
    User Interface for the Activity Planner application.
    Now includes undo/redo functionality.
    """

    def __init__(self, person_service: PersonService, activity_service: ActivityService, undo_redo_service: UndoRedoService):
        """
        Initialize the UI with services.
        
        Args:
            person_service: Service for managing persons
            activity_service: Service for managing activities
            undo_redo_service: Service for undo/redo operations
        """
        self.__person_service = person_service
        self.__activity_service = activity_service
        self.__undo_redo_service = undo_redo_service

    def display_menu(self):
        """Display the main menu with all available commands."""
        print("\n")
        print("=" * 50)
        print("Welcome to Activity Planner")
        print("=" * 50)
        print("Choose one of the following instructions:")
        print("-" * 50)
        print("add person / add activity")
        print("remove person / remove activity")
        print("update person / update activity")
        print("list persons / list activities")
        print("search persons / search activities")
        print("-" * 50)
        print("undo - Undo the last operation")
        print("redo - Redo the last undone operation")
        print("-" * 50)
        print("exit")
        print("=" * 50)
        print("\n")

    def add_person_ui(self):
        """Handle adding a new person through the UI."""
        person_name = input("Enter the name of the person: ")
        person_number = input("Enter the phone number of the person: ")
        try:
            rez = self.__person_service.add_person_from_string(person_name, person_number)
            print(f"✓ Added: {rez}")
        except PersonException as e:
            print(f"✗ Error: {e}")

    def add_activity_ui(self):
        """Handle adding a new activity through the UI."""
        person_ids_input = input("Enter person IDs (comma-separated), or leave empty: ")
        try:
            person_ids = [int(p.strip()) for p in person_ids_input.split(',') if p.strip()]
        except ValueError:
            print("✗ Error: person IDs must be numbers separated by commas.")
            return
        date = input("Enter date (YYYY-MM-DD): ")
        time = input("Enter time (HH:MM): ")
        description = input("Enter description: ")
        try:
            # Use the new method that supports undo/redo
            rez = self.__activity_service.add_activity_with_undo(person_ids, date, time, description)
            print(f"✓ Added: {rez}")
        except ActivityException as e:
            print(f"✗ Error: {e}")

    def list_person_ui(self):
        """Display all registered persons."""
        all_persons = self.__person_service.get_all_service()
        if not all_persons:
            print("No persons registered")
        else:
            print("\n" + "=" * 70)
            print("LIST OF REGISTERED PERSONS")
            print("=" * 70)
            for idx, element in enumerate(all_persons, start=1):
                print(f"{idx}. {element}")
            print("=" * 70)

    def list_activity_ui(self):
        """Display all registered activities with their participants."""
        all_activities = self.__activity_service.get_all_service()
        if not all_activities:
            print("No activity registered")
        else:
            print("\n" + "=" * 70)
            print("LIST OF ACTIVITIES")
            print("=" * 70)
            for idx, activity in enumerate(all_activities, start=1):
                print(f"\n{idx}. ID: {activity.activity_id}, {activity.description} on {activity.date} at {activity.time}")
                if activity.person_id:
                    print("  Participants:")
                    for person_id in activity.person_id:
                        try:
                            person = self.__person_service.get_by_id(person_id)
                            print(f"    - ID: {person.person_id}, Name: {person.name}, Phone: {person.phone_number}")
                        except PersonException as e:
                            print(f"    - Error: {e}")
                else:
                    print("  No participants.")
            print("=" * 70)

    def remove_person_ui(self):
        """Handle removing a person through the UI."""
        name = input("Please write the name of the person that you want to remove -> ")
        try:
            self.__person_service.remove_person(name)
            print(f"✓ Removed successfully: {name}")
            print("  (Note: Person IDs have been removed from all associated activities)")
        except PersonException as e:
            print(f"✗ Error: {e}")

    def remove_activity_ui(self):
        """Handle removing an activity through the UI."""
        id = input("Please write the id of the activity that you want to remove -> ")
        try:
            self.__activity_service.remove_activity(id)
            print(f"✓ Removed successfully: Activity with ID {id}")
        except ActivityException as e:
            print(f"✗ Error: {e}")
        except ValueError:
            print("✗ Error: the activity ID must be a number.")

    def search_person_ui(self):
        """Handle searching for persons through the UI."""
        potential_string = input("Please write the name/phone number for the person you are looking for -> ")
        try:
            person_list = self.__person_service.search_person(potential_string)
            print("✓ Search completed")
            if not person_list:
                print(f"  No persons found with: {potential_string}")
            else:
                print(f"  Found {len(person_list)} person(s):")
                for idx, element in enumerate(person_list, start=1):
                    print(f"  {idx}. {element}")
        except PersonException as e:
            print(f"✗ Error: {e}")

    def search_activity_ui(self):
        """Handle searching for activities through the UI."""
        potential_string = input("Please write the date/time/description for the activity you are looking for -> ")
        try:
            activity_list = self.__activity_service.search_activity(potential_string)
            print("✓ Search completed")
            if not activity_list:
                print(f"  No activities found with: {potential_string}")
            else:
                print(f"  Found {len(activity_list)} activity/activities:")
                for idx, activity in enumerate(activity_list, start=1):
                    print(f"\n  {idx}. ID: {activity.activity_id}, {activity.description} on {activity.date} at {activity.time}")
                    if activity.person_id:
                        print("    Participants:")
                        for person_id in activity.person_id:
                            try:
                                person = self.__person_service.get_by_id(person_id)
                                print(f"      - ID: {person.person_id}, Name: {person.name}, Phone: {person.phone_number}")
                            except PersonException as e:
                                print(f"      - Error: {e}")
                    else:
                        print("    No participants.")
        except ActivityException as e:
            print(f"✗ Error: {e}")

    def update_person_ui(self):
        """Handle updating a person through the UI."""
        try:
            person_id = int(input("Enter the ID of the person to update: "))
            new_name = input("Enter the new name (or press Enter to keep current): ")
            new_phone_number = input("Enter the new phone number (or press Enter to keep current): ")
            updated_person = self.__person_service.update_person(person_id, new_name, new_phone_number)
            print(f"✓ Updated: {updated_person}")
        except PersonException as e:
            print(f"✗ Error: Invalid ID. {e}")
        except ValueError:
            print(f"✗ Error: Invalid ID format. Please enter a number.")
        except Exception as e:
            print(f"✗ Error: {e}")

    def update_activity_ui(self):
        """Handle updating an activity through the UI."""
        try:
            activity_id = int(input("Enter the ID of the activity to update: "))
            person_ids_input = input("Enter new person IDs (comma-separated), or press Enter to keep current: ")
            new_person_ids = [int(p.strip()) for p in person_ids_input.split(',') if p.strip()]
            new_date = input("Enter the new date (YYYY-MM-DD) or press Enter to keep current: ")
            new_time = input("Enter the new time (HH:MM) or press Enter to keep current: ")
            new_description = input("Enter the new description or press Enter to keep current: ")
            updated_activity = self.__activity_service.update_activity(activity_id, new_person_ids, new_date, new_time, new_description)
            print(f"✓ Updated: {updated_activity}")
        except ActivityException as e:
            print(f"✗ Error: Invalid ID. {e}")
        except ValueError:
            print(f"✗ Error: Invalid ID format. Please enter a number.")
        except Exception as e:
            print(f"✗ An unexpected error occurred: {e}")

    def undo_ui(self):
        """Handle undo operation through the UI."""
        try:
            self.__undo_redo_service.undo()
            print("✓ Undo successful - Last operation reversed")
        except IndexError as e:
            print(f"✗ Cannot undo: {e}")

    def redo_ui(self):
        """Handle redo operation through the UI."""
        try:
            self.__undo_redo_service.redo()
            print("✓ Redo successful - Operation restored")
        except IndexError as e:
            print(f"✗ Cannot redo: {e}")

    def main(self):
        """Main loop for the application."""
        while True:
            self.display_menu()
            
            # Show undo/redo status
            if self.__undo_redo_service.can_undo():
                print(f"[Undo available: {self.__undo_redo_service.get_history_size()} operation(s)]")
            if self.__undo_redo_service.can_redo():
                print(f"[Redo available: {self.__undo_redo_service.get_redo_size()} operation(s)]")
            
            user_input = input("Enter your action -> ").strip()
            
            if not user_input:
                print("Please enter a command.")
                continue
            
            parts = user_input.split()
            command = parts[0].lower()
            
            # Handle single-word commands
            if command == 'exit':
                print("Goodbye! :)")
                return
            
            if command == 'undo':
                self.undo_ui()
                continue
            
            if command == 'redo':
                self.redo_ui()
                continue
            
            # Handle two-word commands
            if len(parts) < 2:
                print("Invalid command. Please use format like 'add person' or 'list activities'.")
                continue
            
            subcommand = parts[1].lower()
            
            if command == 'add':
                if subcommand == 'person':
                    self.add_person_ui()
                elif subcommand == 'activity':
                    self.add_activity_ui()
                else:
                    print("Invalid choice. Use 'add person' or 'add activity'.")
            
            elif command == 'list':
                if subcommand == 'persons':
                    self.list_person_ui()
                elif subcommand == 'activities':
                    self.list_activity_ui()
                else:
                    print("Invalid choice. Use 'list persons' or 'list activities'.")
            
            elif command == 'remove':
                if subcommand == 'person':
                    self.remove_person_ui()
                elif subcommand == 'activity':
                    self.remove_activity_ui()
                else:
                    print("Invalid choice. Use 'remove person' or 'remove activity'.")
            
            elif command == 'search':
                if subcommand == 'persons':
                    self.search_person_ui()
                elif subcommand == 'activities':
                    self.search_activity_ui()
                else:
                    print("Invalid choice. Use 'search persons' or 'search activities'.")
            
            elif command == 'update':
                if subcommand == 'person':
                    self.update_person_ui()
                elif subcommand == 'activity':
                    self.update_activity_ui()
                else:
                    print("Invalid choice. Use 'update person' or 'update activity'.")
            
            else:
                print(f"Unknown command: '{command}'. Please try again.")
