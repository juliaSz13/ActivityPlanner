"""
Simplified Command Design Pattern Implementation

This module contains a single, generic Command class that can handle any operation.
Instead of creating separate command classes for each operation, we pass functions
as parameters - much simpler and more flexible!
"""

class Command:
    """
    Generic Command class that works for ANY operation.
    
    Instead of creating AddPersonCommand, RemovePersonCommand, etc.,
    we just create Command objects with different execute/undo functions.
    
    This is much simpler and follows the principle: "Composition over inheritance"
    """
    
    def __init__(self, execute_func, undo_func):
        """
        Initialize a generic command with execute and undo functions.
        
        Args:
            execute_func: A function (or lambda) that performs the operation
            undo_func: A function (or lambda) that reverses the operation
        
        Example:
            # Add person command
            command = Command(
                execute_func=lambda: repo.add_person(person),
                undo_func=lambda: repo.remove_person(person.name)
            )
        """
        self._execute_func = execute_func
        self._undo_func = undo_func
    
    def execute(self):
        """Execute the operation by calling the execute function"""
        self._execute_func()
    
    def undo(self):
        """Undo the operation by calling the undo function"""
        self._undo_func()


