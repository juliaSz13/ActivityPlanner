import os
from typing import List
from domain.Person import Person
import pickle

class MemoryRepository:
    def __init__(self) -> None:
        self.__data: List[Person] = []

    def add_person(self, entity: Person) -> None:
        self.__data.append(entity)

    def get_all(self) -> List[Person]:
        return list(self.__data)

    def remove_person(self, name: str) -> List[Person]:

        new_list = [p for p in self.__data if p.name != name]
        self.__data = new_list
        return self.__data

    def replace_all(self, entities: List[Person]) -> None:
        self.__data = entities

    def search(self, string: str) -> List[Person]:
        return [p for p in self.__data if string.lower() in p.name.lower() or string in p.phone_number]

class TextFileRepository(MemoryRepository):

    def __init__(self, filename: str) -> None:

        super().__init__()
        self.__filename = filename
        if not os.path.exists(self.__filename):
            open(self.__filename, "w").close()


        super().replace_all(self._load_from_file())

    def _load_from_file(self) -> List[Person]:
        entities: List[Person] = []
        with open(self.__filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entities.append(Person.from_text_line(line))
        return entities

    def _save_to_file(self) -> None:

        entities = super().get_all()
        with open(self.__filename, "w", encoding="utf-8") as f:
            for e in entities:
                f.write(e.to_text_line() + "\n")



    def add_person(self, entity: Person):
        super().add_person(entity)
        self._save_to_file()

    def remove_person(self, name: str) -> List[Person]:
        result_list = super().remove_person(name)
        self._save_to_file()
        return result_list

    def replace_all(self, entities: List[Person]) -> None:
        super().replace_all(entities)
        self._save_to_file()




class BinaryFileRepository(MemoryRepository):

    def __init__(self, filename: str) -> None:
        super().__init__()
        self._filename = filename

        if not os.path.exists(self._filename):
            with open(self._filename, "wb") as f:
                pickle.dump([], f)


        initial_data = self._load_from_file()
        super().replace_all(initial_data)

    def _load_from_file(self) -> List[Person]:
        try:
            with open(self._filename, "rb") as f:
                data = pickle.load(f)
                return list(data)
        except (EOFError, pickle.UnpicklingError):
            return []

    def _save_to_file(self, entities: List[Person]) -> None:
        with open(self._filename, "wb") as f:
            pickle.dump(entities, f)



    def add_person(self, entity: Person) -> None:
        super().add_person(entity)
        self._save_to_file(super().get_all())

    def remove_person(self, name: str) -> List[Person]:
        result_list = super().remove_person(name)
        self._save_to_file(result_list)
        return result_list

    def replace_all(self, entities: List[Person]) -> None:
        super().replace_all(entities)
        self._save_to_file(entities)

