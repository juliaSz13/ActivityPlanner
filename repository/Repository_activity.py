import os
from typing import List
from domain.Activity import Activity
import pickle


class MemoryRepository:

    def __init__(self) -> None:
        self.__data: List[Activity] = []

    def get_all(self) -> List[Activity]:
        return self.__data

    def replace_all(self, entities: List[Activity]) -> None:
        self.__data = entities

    def add_activity(self, entity: Activity) -> None:
        self.__data.append(entity)

    def remove_activity(self, id: str) -> List[Activity]:
        new_list = [a for a in self.__data if a.activity_id != int(id)]
        self.__data = new_list

        return self.__data

    def search(self, string: str) -> List[Activity]:
        return [a for a in self.__data if string in a.date or string in a.time or string in a.description]


class TextFileRepository(MemoryRepository):

    def __init__(self, filename: str) -> None:
        super().__init__()
        self.__filename = filename

        if not os.path.exists(self.__filename):
            open(self.__filename, "w").close()

        super().replace_all(self._load_from_file())

    def _load_from_file(self) -> List[Activity]:
        entities: List[Activity] = []
        with open(self.__filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entities.append(Activity.from_text_line(line))
        return entities

    def _save_to_file(self) -> None:
        entities = super().get_all()
        with open(self.__filename, "w", encoding="utf-8") as f:
            for e in entities:
                f.write(e.to_text_line() + "\n")



    def add_activity(self, entity: Activity):
        super().add_activity(entity)
        self._save_to_file()

    def replace_all(self, entities: List[Activity]):
        super().replace_all(entities)
        self._save_to_file()

    def remove_activity(self, id: str):
        result_list = super().remove_activity(id)
        self._save_to_file()
        return result_list




class BinaryFileRepository(MemoryRepository):

    def __init__(self, filename: str) -> None:
        super().__init__()
        self._filename = filename

        if not os.path.exists(self._filename):
            with open(self._filename, "wb") as f:
                pickle.dump([], f)
        super().replace_all(self._load_from_file())

    def _load_from_file(self) -> List[Activity]:
        try:
            with open(self._filename, "rb") as f:
                data = pickle.load(f)
                return data
        except (EOFError, pickle.UnpicklingError):
            return []

    def _save_to_file(self) -> None:
        entities = super().get_all()
        with open(self._filename, "wb") as f:
            pickle.dump(entities, f)

    def add_activity(self, entity: Activity) -> None:
        super().add_activity(entity)
        self._save_to_file()

    def replace_all(self, entities: List[Activity]):
        super().replace_all(entities)
        self._save_to_file()

    def remove_activity(self, description: str):
        result_list = super().remove_activity(description)
        self._save_to_file()
        return result_list
