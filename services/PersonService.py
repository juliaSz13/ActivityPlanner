from faker import Faker
from repository.Repository_person import MemoryRepository
from domain.Person import Person
from Command import Command

class PersonException(Exception):
    pass


class PersonService:
    """
    Manages operations related to Person entities.
    Now uses the simplified generic Command class!
    """
    
    def __init__(self, repo: MemoryRepository, activity_service, undo_redo_service=None):
        self.__person_repo = repo
        self.__activity_service = activity_service
        self.__undo_redo_service = undo_redo_service
        self.ensure_person_data()

    def ensure_person_data(self) -> None:
        """Generate initial fake data if repository is empty."""
        if len(self.__person_repo.get_all()) > 0:
            return
        fake = Faker()
        for i in range(1, 21):
            self.add_person(i, fake.name(), fake.numerify("07########"))

    def generate_new_id(self):
        """Generate the next available unique integer ID."""
        persons = self.__person_repo.get_all()
        if not persons:
            return 1
        max_id = max(person.person_id for person in persons)
        return max_id + 1

    def add_person(self, person_id: int, name: str, phone_number: str):
        """Add a person directly (without undo/redo) - used for initial data."""
        new_person = Person(person_id, name, phone_number)
        self.__person_repo.add_person(new_person)

    def add_person_from_string(self, person_name: str, person_phone_number: str):
        """
        Add a new person with undo/redo support.
        Uses the generic Command class with lambda functions!
        """
        if not (len(person_phone_number) == 11 or len(person_phone_number) == 10):
            raise PersonException("the length of the phone number must be 11 or 10")
        
        person_id = self.generate_new_id()
        new_person = Person(person_id, person_name, person_phone_number)
        
        if self.__undo_redo_service:
            # Create a generic Command with lambda functions
            command = Command(
                execute_func=lambda: self.__person_repo.add_person(new_person),
                undo_func=lambda: self.__person_repo.remove_person(new_person.name)
            )
            self.__undo_redo_service.execute_command(command)
        else:
            self.__person_repo.add_person(new_person)
        
        return new_person

    def get_all_service(self):
        """Get all persons."""
        return self.__person_repo.get_all()

    def get_by_id(self, person_id: int) -> Person:
        """Find a person by ID."""
        for person in self.get_all_service():
            if person.person_id == person_id:
                return person
        raise PersonException(f"Person with id {person_id} not found")

    def get_all_person_ids(self) -> list[int]:
        """Get list of all person IDs."""
        all_persons = self.get_all_service()
        return [person.person_id for person in all_persons]

    def remove_person(self, name: str) -> list[Person]:
        """
        Remove a person with cascading deletion and undo/redo support.
        Uses the generic Command class!
        """
        if self.__undo_redo_service:
            # We need to capture the state BEFORE deletion for undo
            # Store what we need for undo in a closure
            persons_to_delete = [p for p in self.__person_repo.get_all() if p.name == name]
            
            if not persons_to_delete:
                raise PersonException(f"Person with name '{name}' not found.")
            
            deleted_ids = [p.person_id for p in persons_to_delete]
            modified_activities = []  # Will store (activity, original_person_ids)
            
            def execute_remove():
                """Execute function: Remove person and cascade to activities"""
                # Remove person
                self.__person_repo.remove_person(name)
                
                # Cascade to activities
                all_activities = self.__activity_service.get_all_service()
                for activity in all_activities:
                    original_person_ids = list(activity.person_id)
                    new_person_ids = [pid for pid in activity.person_id if pid not in deleted_ids]
                    
                    if len(new_person_ids) < len(original_person_ids):
                        # Store for undo
                        modified_activities.append((activity, original_person_ids))
                        activity.person_id = new_person_ids
                
                # Save changes
                if modified_activities:
                    self.__activity_service.get_repo().replace_all(all_activities)
            
            def undo_remove():
                """Undo function: Restore person and activities"""
                # Restore persons
                for person in persons_to_delete:
                    self.__person_repo.add_person(person)
                
                # Restore activities
                for activity, original_person_ids in modified_activities:
                    activity.person_id = original_person_ids
                
                # Save changes
                if modified_activities:
                    all_activities = self.__activity_service.get_all_service()
                    self.__activity_service.get_repo().replace_all(all_activities)
            
            # Create generic command
            command = Command(execute_func=execute_remove, undo_func=undo_remove)
            self.__undo_redo_service.execute_command(command)
            
            return persons_to_delete
        else:
            # Fallback without undo/redo
            persons_to_delete = [p for p in self.__person_repo.get_all() if p.name == name]
            if not persons_to_delete:
                raise PersonException(f"Person with name '{name}' not found.")
            
            deleted_ids = [p.person_id for p in persons_to_delete]
            self.__person_repo.remove_person(name)
            
            all_activities = self.__activity_service.get_all_service()
            for activity in all_activities:
                new_person_ids = [pid for pid in activity.person_id if pid not in deleted_ids]
                if len(new_person_ids) < len(activity.person_id):
                    self.__activity_service.update_activity_participants(activity.activity_id, new_person_ids)
            
            return persons_to_delete

    def update_person(self, person_id: int, new_name: str, new_phone_number: str) -> Person:
        """
        Update a person with undo/redo support.
        Uses the generic Command class!
        """
        if self.__undo_redo_service:
            # Find the person
            persons = self.__person_repo.get_all()
            person_to_update = None
            for person in persons:
                if person.person_id == person_id:
                    person_to_update = person
                    break
            
            if person_to_update is None:
                raise PersonException(f"Person with id {person_id} not found.")
            
            # Store original values (in closure)
            original_name = person_to_update.name
            original_phone = person_to_update.phone_number
            
            def execute_update():
                """Execute function: Update the person"""
                if new_name:
                    person_to_update.name = new_name
                if new_phone_number:
                    person_to_update.phone_number = new_phone_number
                self.__person_repo.replace_all(persons)
            
            def undo_update():
                """Undo function: Restore original values"""
                person_to_update.name = original_name
                person_to_update.phone_number = original_phone
                self.__person_repo.replace_all(persons)
            
            # Create generic command
            command = Command(execute_func=execute_update, undo_func=undo_update)
            self.__undo_redo_service.execute_command(command)
            
            return person_to_update
        else:
            # Fallback without undo/redo
            persons = self.__person_repo.get_all()
            person_to_update = None
            for person in persons:
                if person.person_id == person_id:
                    person_to_update = person
                    break
            
            if person_to_update is None:
                raise PersonException(f"Person with id {person_id} not found.")
            
            if new_name:
                person_to_update.name = new_name
            if new_phone_number:
                person_to_update.phone_number = new_phone_number
            
            self.__person_repo.replace_all(persons)
            return person_to_update

    def search_person(self, string: str):
        """Search for persons by name or phone number."""
        if len(string) < 3:
            raise PersonException("the length of the potential name or phone number must be at least 3")
        return self.__person_repo.search(string)
