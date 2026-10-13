"""
Undo/Redo Service Module

This module provides the UndoRedoService class which manages the command history
and provides undo/redo functionality for the Activity Planner application.

The service maintains two stacks:
- history: Stack of executed commands (for undo)
- redo_stack: Stack of undone commands (for redo)
"""

from typing import List
from Command import Command


class UndoRedoService:
    """
    Manages undo/redo functionality using the Command pattern.
    
    This service maintains two stacks:
    1. history: Commands that have been executed (can be undone)
    2. redo_stack: Commands that have been undone (can be redone)
    
    Memory-efficient implementation: Only stores command objects, not entire
    data snapshots.
    """
    
    def __init__(self):
        """Initialize the undo/redo service with empty stacks"""
        self._history: List[Command] = []  # Stack of executed commands
        self._redo_stack: List[Command] = []  # Stack of undone commands
    
    def execute_command(self, command: Command):
        """
        Execute a command and add it to the history.
        
        This method:
        1. Executes the command
        2. Adds it to the history stack
        3. Clears the redo stack (since we're on a new timeline)
        
        Args:
            command: The Command object to execute
        """
        command.execute()
        self._history.append(command)
        # Clear redo stack when a new command is executed
        # (you can't redo after doing something new)
        self._redo_stack.clear()
    
    def undo(self):
        """
        Undo the last executed command.
        
        This method:
        1. Checks if there's anything to undo
        2. Pops the last command from history
        3. Calls its undo() method
        4. Pushes it to the redo stack
        
        Raises:
            IndexError: If there are no commands to undo
        """
        if not self._history:
            raise IndexError("No operations to undo")
        
        # Pop the last command from history
        command = self._history.pop()
        
        # Undo the command
        command.undo()
        
        # Add to redo stack so it can be redone later
        self._redo_stack.append(command)
    
    def redo(self):
        """
        Redo the last undone command.
        
        This method:
        1. Checks if there's anything to redo
        2. Pops the last command from redo stack
        3. Calls its execute() method again
        4. Pushes it back to the history stack
        
        Raises:
            IndexError: If there are no commands to redo
        """
        if not self._redo_stack:
            raise IndexError("No operations to redo")
        
        # Pop the last undone command
        command = self._redo_stack.pop()
        
        # Re-execute the command
        command.execute()
        
        # Add back to history
        self._history.append(command)
    
    def can_undo(self) -> bool:
        """
        Check if undo is available.
        
        Returns:
            bool: True if there are commands that can be undone
        """
        return len(self._history) > 0
    
    def can_redo(self) -> bool:
        """
        Check if redo is available.
        
        Returns:
            bool: True if there are commands that can be redone
        """
        return len(self._redo_stack) > 0
    
    def get_history_size(self) -> int:
        """
        Get the number of commands in the history.
        
        Returns:
            int: The number of undoable commands
        """
        return len(self._history)
    
    def get_redo_size(self) -> int:
        """
        Get the number of commands in the redo stack.
        
        Returns:
            int: The number of redoable commands
        """
        return len(self._redo_stack)
    
    def clear_history(self):
        """
        Clear both history and redo stacks.
        
        This might be useful when starting a new session or after
        loading data from a file.
        """
        self._history.clear()
        self._redo_stack.clear()
