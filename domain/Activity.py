
from datetime import datetime
import ast
class Activity:

    def __init__(self,activity_id:int,person_ids:list,date:str,time:str, description:str)->None:
         self.__activity_id=activity_id
         self.__person_ids=person_ids
         self.__date=date
         self.__time=time
         self.__description=description

    @property
    def person_id(self)->list:
        return self.__person_ids

    @property
    def activity_id(self)->int:
        return self.__activity_id

    @property
    def date(self)->str:
        return self.__date

    @property
    def time(self)->str:
        return self.__time

    @property
    def description(self)->str:
        return self.__description

    @person_id.setter
    def person_id(self, new_person_ids: list) -> None:
        if not isinstance(new_person_ids, list):
            raise TypeError("Person IDs must be a list.")
        self.__person_ids = new_person_ids

    @date.setter
    def date(self,new_date:str)->None:
        date_format="%Y-%m-%d"
        try:
            datetime.strptime(new_date,date_format)
        except ValueError:
            raise ValueError("the date must be like YYYY-MM-DD")
        self.__date=new_date

    @time.setter
    def time(self, new_time:str)->None:
         time_format="%H:%M"
         try:
            datetime.strptime(new_time,time_format)
         except ValueError:
             raise ValueError("invalid format for the time. It must be like HH:MM")
         self.__time=new_time


    @description.setter
    def description(self,new_description:str)->None:
        if not isinstance(new_description,str) or len(new_description.strip())==0:
            raise TypeError("The description must be a non-empty string")
        self.__description=new_description


    def __str__(self):
        participants=f"[{'.'.join(map(str,self.__person_ids))}]" if self.__person_ids else "None"
        return f"ID:{self.__activity_id}| PARTICIPANTS:{participants}| DATE: { self.__date}| TIME: {self.__time} | DESCRIPTION:{self.__description}"

    def __repr__(self):
        return (f"Activity(id={self.__activity_id!r}, person_ids={self.__person_ids!r}, "
                f"date={self.__date!r}, time={self.__time!r}, "
                f"description={self.__description!r})")

    def __eq__(self, other):
        if not isinstance(other,Activity):
             return False
        return self.__activity_id==other.activity_id

    def to_text_line(self) -> str:
        participants = repr(self.__person_ids)
        return f"{self.__activity_id};{participants};{self.__date};{self.__time};{self.__description}"

    @staticmethod
    def from_text_line(line: str) -> "Activity":
        parts = line.strip().split(";",4)
        if len(parts) != 5:
            raise ValueError("invalid line for activity")
        activity_id, person_id, date,time,description = parts
        activity_id=int(activity_id)
        person_id=ast.literal_eval(person_id)
        return Activity(activity_id, person_id ,date,time,description)
