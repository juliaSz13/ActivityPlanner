from domain.Activity import Activity
from faker import Faker
from repository.Repository_activity import MemoryRepository
from Command import Command
import random

class ActivityException(Exception):
    pass

class ActivityService:
    """
    Manages operations related to Activity entities.
    Now uses the simplified generic Command class!
    """
    
    def __init__(self, repo: MemoryRepository, undo_redo_service=None):
        self.__repo = repo
        self.__undo_redo_service = undo_redo_service
        self.ensure_activity_date()

    def ensure_activity_date(self):
        """Generate initial fake data if repository is empty."""
        if len(self.__repo.get_all()) > 0:
            return
        fake = Faker()
        activities = ["swimming", "football", "learning", "dancing", "running"]
        for i in range(1, 21):
            person_id = self.generate_list_id()
            self.add_activity(i, person_id, fake.date(), fake.time("%H:%M"), random.choice(activities))

    def generate_list_id(self) -> list:
        """Generate a random list of unique Person IDs."""
        person_id = []
        end = random.randint(1, 18)
        fr = [0] * 21
        j = 1
        while j < end:
            x = random.randint(1, 20)
            if fr[x] == 0:
                person_id.append(x)
                fr[x] = 1
                j += 1
        return person_id

    def generate_new_id(self):
        """Generate the next sequential unique ID for a new activity."""
        activities = self.__repo.get_all()
        if not activities:
            return 1
        max_id = max(activity.activity_id for activity in activities)
        return max_id + 1

    def add_activity(self, activity_id: int, person_id: list, date: str, time: str, description: str):
        """
        Add an activity directly (without undo/redo) - used for initial data.
        Checks for scheduling conflicts.
        """
        all_activities = self.__repo.get_all()
        for activity in all_activities:
            is_the_same_time = (date == activity.date and time == activity.time)
            if is_the_same_time:
                common_ids = [pid for pid in person_id if pid in activity.person_id]
                if len(common_ids) > 0:
                    raise ActivityException(
                        f"Conflict! The persons with the id's {common_ids} aren't available "
                        f"'{activity.description}' at the date {date} at the time {time}."
                    )

        new_activity = Activity(activity_id, person_id, date, time, description)
        self.__repo.add_activity(new_activity)
        return new_activity

    def add_activity_with_undo(self, person_id: list, date: str, time: str, description: str):
        """
        Add a new activity with undo/redo support.
        Uses the generic Command class with lambda functions!
        """
        # Check for conflicts first
        all_activities = self.__repo.get_all()
        for activity in all_activities:
            is_the_same_time = (date == activity.date and time == activity.time)
            if is_the_same_time:
                common_ids = [pid for pid in person_id if pid in activity.person_id]
                if len(common_ids) > 0:
                    raise ActivityException(
                        f"Conflict! The persons with the id's {common_ids} aren't available "
                        f"'{activity.description}' at the date {date} at the time {time}."
                    )
        
        # Generate new ID and create activity
        activity_id = self.generate_new_id()
        new_activity = Activity(activity_id, person_id, date, time, description)
        
        if self.__undo_redo_service:
            # Create a generic Command with lambda functions
            command = Command(
                execute_func=lambda: self.__repo.add_activity(new_activity),
                undo_func=lambda: self.__repo.remove_activity(str(new_activity.activity_id))
            )
            self.__undo_redo_service.execute_command(command)
        else:
            self.__repo.add_activity(new_activity)
        
        return new_activity

    def get_all_service(self):
        """Get all activities."""
        return self.__repo.get_all()
    
    def get_repo(self):
        """Get the repository (needed for cascading operations in PersonService)."""
        return self.__repo

    def remove_activity(self, id: str) -> None:
        """
        Remove an activity with undo/redo support.
        Uses the generic Command class!
        """
        if self.__undo_redo_service:
            # Find the activity before removing it
            all_activities = self.__repo.get_all()
            removed_activity = None
            
            for activity in all_activities:
                if activity.activity_id == int(id):
                    removed_activity = activity
                    break
            
            if removed_activity is None:
                raise ActivityException(f"Activity with id '{id}' not found.")
            
            # Create generic command
            command = Command(
                execute_func=lambda: self.__repo.remove_activity(id),
                undo_func=lambda: self.__repo.add_activity(removed_activity)
            )
            self.__undo_redo_service.execute_command(command)
        else:
            # Fallback without undo/redo
            initial_activities = self.__repo.get_all()
            new_data = self.__repo.remove_activity(id)
            if len(initial_activities) == len(new_data):
                raise ActivityException(f"Activity with id '{id}' not found.")
            self.__repo.replace_all(new_data)

    def update_activity(self, activity_id: int, new_person_ids: list, new_date: str, new_time: str, new_description: str) -> Activity:
        """
        Update an activity with undo/redo support.
        Uses the generic Command class!
        """
        if self.__undo_redo_service:
            # Find the activity
            activities = self.__repo.get_all()
            activity_to_update = None
            
            for activity in activities:
                if activity.activity_id == activity_id:
                    activity_to_update = activity
                    break
            
            if activity_to_update is None:
                raise ActivityException(f"Activity with id {activity_id} not found.")
            
            # Store original values (in closure)
            original_person_ids = list(activity_to_update.person_id)
            original_date = activity_to_update.date
            original_time = activity_to_update.time
            original_description = activity_to_update.description
            
            def execute_update():
                """Execute function: Update the activity"""
                if new_person_ids:
                    activity_to_update.person_id = new_person_ids
                if new_date:
                    activity_to_update.date = new_date
                if new_time:
                    activity_to_update.time = new_time
                if new_description:
                    activity_to_update.description = new_description
                self.__repo.replace_all(activities)
            
            def undo_update():
                """Undo function: Restore original values"""
                activity_to_update.person_id = original_person_ids
                activity_to_update.date = original_date
                activity_to_update.time = original_time
                activity_to_update.description = original_description
                self.__repo.replace_all(activities)
            
            # Create generic command
            command = Command(execute_func=execute_update, undo_func=undo_update)
            self.__undo_redo_service.execute_command(command)
            
            return activity_to_update
        else:
            # Fallback without undo/redo
            activities = self.__repo.get_all()
            activity_to_update = None
            
            for activity in activities:
                if activity.activity_id == activity_id:
                    activity_to_update = activity
                    break
            
            if activity_to_update is None:
                raise ActivityException(f"Activity with id {activity_id} not found.")
            
            if new_person_ids:
                activity_to_update.person_id = new_person_ids
            if new_date:
                activity_to_update.date = new_date
            if new_time:
                activity_to_update.time = new_time
            if new_description:
                activity_to_update.description = new_description
            
            self.__repo.replace_all(activities)
            return activity_to_update

    def search_activity(self, string: str):
        """Search for activities by date, time, or description."""
        if len(string) < 3:
            raise ActivityException("the length of the potential name or phone number must be at least 3")
        return self.__repo.search(string)

    def update_activity_participants(self, activity_id: int, new_person_ids: list):
        """
        Update only the participants of an activity.
        Used internally for cascade operations (doesn't use undo/redo).
        """
        activities = self.__repo.get_all()
        activity_to_update = None

        for activity in activities:
            if activity.activity_id == activity_id:
                activity_to_update = activity
                break

        if activity_to_update is None:
            print(f"The activity with the ID {activity_id} wasn't found.")
            return

        activity_to_update.person_id = new_person_ids
        self.__repo.replace_all(activities)

        return activity_to_update
