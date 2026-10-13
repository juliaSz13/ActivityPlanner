
class Person:
     def __init__(self,person_id:int,name:str,phone_number:str):
         self.__person_id=person_id
         self.__name=name
         self.__phone_number=phone_number

     @property
     def person_id(self):
         return self.__person_id

     @property
     def name(self):
         return self.__name

     @property
     def phone_number(self):
         return self.__phone_number

     @name.setter
     def name(self,new_name):
         if not isinstance(new_name,str) or len(new_name.strip())==0:
             raise ValueError("Name must be non-empty string")
         self.__name=new_name

     @phone_number.setter
     def phone_number(self, new_phone_number: str):
         if not isinstance(new_phone_number, str) or len(new_phone_number.strip()) not in [10, 11]:
             raise ValueError("The phone number must be a string of 10 or 11 digits.")
         self.__phone_number = new_phone_number.strip()

     def __str__(self):
         return f"ID:{self.__person_id} | NAME:{self.__name} | PHONE NUMBER:{self.__phone_number}"

     def __repr__(self):
         return f"Person(id={self.__person_id!r},name={self.__name!r}, phone_number={self.__phone_number!r})"

     def __eq__(self,other):
         if not isinstance(other,Person):
             return False
         return self.__person_id==other.__person_id

     def to_text_line(self)->str:
         return f"{self.__person_id},{ self.__name},{self.__phone_number}"


     @staticmethod
     def from_text_line(line:str)->"Person":
         parts=line.strip().split(",")
         if len(parts)!=3:
             raise ValueError("invalid line for person")
         person_id,name,phone_number=parts
         person_id=int(person_id)
         return Person(person_id,name,phone_number)

