from pydantic import BaseModel, EmailStr, field_validator, Field
from datetime import datetime, date, time
from typing import Optional, List
from models import BookingStatus
import phonenumbers as phone
from phonenumbers.phonenumberutil import NumberParseException


#Job Type Schemas
class JobBase(BaseModel):
    """
    Docstring for JobBase
    title: string names the job type
    """
    title: str = Field(max_length = 20)

class JobCreate(JobBase):
    """
    Docstring for JobCreate
    """
    


class JobResponse(JobBase):
    """
    Docstring for JobResponse
    id is the generated id from the database
    """
    id: int

    class Config:
        from_attributes = True


#Employee Schemas
class EmployeeBase(BaseModel):
    """
    Docstring for EmployeeBase
    name: string of employee name
    phone: string phone number
    email: EmailStr email address
    """
    name: str = Field(max_length=50)
    phone_number: str = Field(max_length=15)
    email: EmailStr = Field(max_length=50)

class EmployeeCreate(EmployeeBase):
    """
    Docstring for EmployeeCreate
    hire_date: date when the employee was hired
    """
    hire_date: date


    @field_validator('phone_number')
    def validate_phone_number(cls, num):
        """
        Docstring for validate_phone_number
        
        :param cls: class EmployeeCreate
        :param num: string of the number input
        raise ValueError if invalid
        """
        default_region = "US"

        #parse phone number
        parsed_phone_num = phone.parse(num, default_region)

        # checks valid phone number
        if phone.is_valid_number(parsed_phone_num):

            #converting to string
            normalized_num = phone.format_number(parsed_phone_num, phone.PhoneNumberFormat.E164)
            return normalized_num
        else:
            raise ValueError("Invalid Phone Number")  

            


class EmployeeResponse(EmployeeBase):
    """
    Docstring for EmployeeResponse
    id: int that database generates
    """
    id: int

    class Config:
        from_attributes = True

#TODO: figure out how we are going to deal with requesting the assigned jobs data -> maybe in org_service


#Address Schemas
class AddressBase(BaseModel):
    #TODO: is this right?
    pass

class AddressCreate(BaseModel):
    """
    Docstring for AddressCreate
    street_number: string number of street
    street_name: string of name of street
    city: string of name of city
    state: string of name of state (abbrev.)
    zip_code: string of zip code
    """
    street_number: str = Field(max_length=10)
    street_name: str = Field(max_length=50)
    city: str = Field(max_length=20)
    state: str = Field(max_length=2)
    zip_code: str = Field(max_length=5)

class AddressResponse(BaseModel):
    """
    Docstring for AddressResponse
    id: integer id created by database
    client: client tied to the address
    """
    id: int
    client: str

    class Config:
        from_attributes = True
    

#client schemas
class ClientBase(BaseModel):
    """
    Docstring for ClientBase
    name: string of name
    phone_number: string of phone number
    email: EmailStr email address
    """
    name: str = Field(max_length=50)
    phone_number: str = Field(max_length=15)
    email: EmailStr = Field(max_length=50)
    

class ClientCreate(ClientBase):
    """
    Docstring for ClientCreate
    address_id: foreign key id mapped to an address
    """
    address_id: int

    @field_validator('phone_number')
    def validate_phone_number(cls, num):
        """
        Docstring for validate_phone_number
        
        :param cls: class EmployeeCreate
        :param num: string of the number input
        raise ValueError if invalid
        """
        default_region = "US"

        #parse phone number
        parsed_phone_num = phone.parse(num, default_region)

        # checks valid phone number
        if phone.is_valid_number(parsed_phone_num):
            
            #converting to string
            normalized_num = phone.format_number(parsed_phone_num, phone.PhoneNumberFormat.E164)
            return normalized_num
        else:
            raise ValueError("Invalid Phone Number")  


class ClientResponse(ClientBase):
    """
    Docstring for ClientResponse
    address: address linked to client
    """
    address: str

    class Config:
        from_attributes = True



#confirmed booking schemas
class ConfirmedBookingBase(BaseModel):
    """
    Docstring for ConfirmedBookingBase
    date: date of booking
    start_time: time of start
    end_time: time of end
    status: backend.models.BookingStatus enumeration
    """
    date: date
    start_time: time
    end_time: time
    status: BookingStatus

class ConfirmedBookingCreate(ConfirmedBookingBase):
    """
    address_id: integer foreign key mapped to an address
    client: integer foreign key mapped to a client
    assigned_employees: integer list of employees assigned to booking
    """
    address_id: int
    client_id: int
    assigned_employees: list[int]

    @field_validator('assigned_employees')
    def validate_assigned_employees(cls, employee_list):
        """
        Docstring for validate_assigned_employees
        
        :param cls: ConfirmedBookingCreate class
        :param employee_list: list of employees
        raises ValueError if there are duplicates
        """
        if len(employee_list) != len(set(employee_list)):
            raise ValueError('There are duplicate employees')
        
        return employee_list
    

class ConfirmedBookingResponse(ConfirmedBookingBase):
    """
    Docstring for ConfirmedBookingResponse
    created_at: time of creation
    updated_at: time of update
    id_hash: hash code of booking
    """
    created_at: datetime
    updated_at: datetime
    id_hash: str

    class Config: 
        from_attributes = True


