# Activity Planner

A console application in Python for planning activities between people. You can add, update, remove, list and search people and activities, and undo or redo any change.

## Features

- **Layered architecture:** domain, repository, service and UI layers, each with its own responsibility
- **Three storage options:** in memory, text file or binary file (pickle), chosen in `application.properties`
- **Undo / redo** for every operation, built with the **Command design pattern**. Removing a person also removes them from their activities, and undo restores both.
- **Scheduling conflict detection:** a person can't be in two activities at the same date and time
- **Unit tests** with `unittest` and mocking
- Sample data generated with the [Faker](https://faker.readthedocs.io/) library on first run

## Project structure

```
activity-planner/
├── main.py                  # entry point: reads the config and connects the layers
├── application.properties   # storage settings
├── Command.py               # generic Command class (execute / undo)
├── UndoRedoService.py       # undo and redo stacks
├── domain/                  # Person, Activity
├── repository/              # memory, text file and binary file repositories
├── services/                # business logic + undo/redo commands
├── ui/                      # console menu
└── tests/                   # unit tests
```

## How to run

You need Python 3.9 or newer.

```bash
pip install -r requirements.txt
python main.py
```

Then type commands such as `add person`, `list activities`, `undo` or `exit`.

To change how data is stored, edit `repository_type` in `application.properties` (`memory`, `text` or `binary`).

## How to run the tests

From the project folder:

```bash
python -m unittest discover -s tests -t .
```
