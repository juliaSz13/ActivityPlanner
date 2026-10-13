import sys
from pathlib import Path
from typing import Dict, Any

from repository.Repository_person import (
    MemoryRepository as PersonMemoryRepo,
    TextFileRepository as PersonTextRepo,
    BinaryFileRepository as PersonBinaryRepo,
)
from repository.Repository_activity import (
    MemoryRepository as ActivityMemoryRepo,
    TextFileRepository as ActivityTextRepo,
    BinaryFileRepository as ActivityBinaryRepo,
)

from services.ActivityService import ActivityService
from services.PersonService import PersonService
from ui.ui import UI
from UndoRedoService import UndoRedoService


def _load_properties(filename: str) -> Dict[str, str]:
    """
    Load configuration from a properties file.
    
    Args:
        filename: Name of the properties file
        
    Returns:
        Dict[str, str]: Dictionary of configuration key-value pairs
        
    Raises:
        FileNotFoundError: If the properties file doesn't exist
    """
    base_dir = Path(__file__).resolve().parent
    path = base_dir / filename

    props: Dict[str, str] = {}
    if not path.exists():
        raise FileNotFoundError(f"The file '{filename}' wasn't found.")

    with path.open("r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#") or line.startswith(";"):
                continue
            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            props[key.strip()] = value.strip()

    return props


def _get_file_extension(repo_type: str) -> str:
    """
    Get the appropriate file extension for the repository type.
    
    Args:
        repo_type: Type of repository ('text', 'binary', or 'memory')
        
    Returns:
        str: File extension ('.txt', '.pickle', or empty string)
    """
    if repo_type == "text":
        return ".txt"
    elif repo_type == "binary":
        return ".pickle"
    return ""


def build_app() -> UI:
    """
    Build and configure the entire application with dependency injection.
    
    This function:
    1. Loads configuration from application.properties
    2. Creates the appropriate repositories based on configuration
    3. Creates the undo/redo service
    4. Creates the activity and person services with undo/redo support
    5. Creates and returns the UI
    
    Returns:
        UI: The configured user interface
        
    Raises:
        FileNotFoundError: If application.properties is not found
    """
    try:
        props = _load_properties("application.properties")
    except FileNotFoundError as e:
        print(f"\nERROR: {e}")
        sys.exit(1)

    repo_type = props.get("repository_type", "memory").lower()

    person_filename_base = props.get("person_repo_file", "person_data").strip()
    activity_filename_base = props.get("activity_repo_file", "activity_data").strip()

    ext = _get_file_extension(repo_type)
    base_dir = Path(__file__).resolve().parent

    # ========================================================================
    # Create Undo/Redo Service (shared by both Person and Activity services)
    # ========================================================================
    print("[INFO] Creating UndoRedoService for undo/redo functionality")
    undo_redo_service = UndoRedoService()

    # ========================================================================
    # Build Activity Repository and Service
    # ========================================================================
    activity_repo: Any

    if repo_type == "memory":
        print("[INFO] Building Activity using MemoryRepository.")
        activity_repo = ActivityMemoryRepo()

    elif repo_type == "text":
        filename = str(base_dir / (activity_filename_base + ext))
        print(f"[INFO] Building Activity using TextFileRepository. File: {filename}")
        activity_repo = ActivityTextRepo(filename)

    elif repo_type == "binary":
        filename = str(base_dir / (activity_filename_base + ext))
        print(f"[INFO] Building Activity using BinaryFileRepository. File: {filename}")
        activity_repo = ActivityBinaryRepo(filename)

    else:
        print(f"[WARN] repository type '{repo_type}' unknown. Using memory repository for activity.")
        activity_repo = ActivityMemoryRepo()

    # Create ActivityService with undo/redo support
    activity_service = ActivityService(activity_repo, undo_redo_service)

    # ========================================================================
    # Build Person Repository and Service
    # ========================================================================
    person_repo: Any

    if repo_type == "memory":
        print("[INFO] Building Person using MemoryRepository.")
        person_repo = PersonMemoryRepo()

    elif repo_type == "text":
        filename = str(base_dir / (person_filename_base + ext))
        print(f"[INFO] Building Person using TextFileRepository. File: {filename}")
        person_repo = PersonTextRepo(filename)

    elif repo_type == "binary":
        filename = str(base_dir / (person_filename_base + ext))
        print(f"[INFO] Building Person using BinaryFileRepository. File: {filename}")
        person_repo = PersonBinaryRepo(filename)

    else:
        print(f"[WARN] repository type '{repo_type}' unknown. Using memory repository for person.")
        person_repo = PersonMemoryRepo()

    # Create PersonService with undo/redo support
    person_service = PersonService(person_repo, activity_service, undo_redo_service)

    # ========================================================================
    # Build UI with all services
    # ========================================================================
    print("[INFO] Building UI with undo/redo functionality")
    return UI(person_service, activity_service, undo_redo_service)


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("ACTIVITY PLANNER - With Undo/Redo Support")
    print("=" * 70)
    
    ui = build_app()
    
    print("\n✅ Application initialized successfully. Starting UI.")
    print("=" * 70)
    
    ui.main()
