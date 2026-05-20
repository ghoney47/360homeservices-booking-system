from pydantic import BaseModel, EmailStr, field_validator, Field
from datetime import datetime, date, time
from typing import Optional
from models import BookingStatus
from utils import validators as val


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
    """
    pass

class EmployeeCreate(EmployeeBase):
    """
    Docstring for EmployeeCreate
    hire_date: date when the employee was hired
    name: string of employee name
    phone: string phone number
    email: EmailStr email address
    """
    hire_date: date
    name: str = Field(max_length=50)
    phone_number: str = Field(max_length=15)
    email: EmailStr = Field(max_length=50)


    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, num):
        """
        passes phone number to validator
        """
        return val.validate_phone_number(num)
        
class EmployeeUpdate(EmployeeBase):
    phone_number: Optional[str] = Field(max_length=15)
    email: Optional[EmailStr] = Field(max_length=50)

    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, num):
        if num is None:
            return num
        else: 
            return val.validate_phone_number(num)

class EmployeeResponse(EmployeeBase):
    """
    Docstring for EmployeeResponse
    id: int that database generates
    """
    id: int
    name: str

    class Config:
        from_attributes = True


#Address Schemas
class AddressBase(BaseModel):
    pass

class AddressCreate(AddressBase):
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

class AddressUpdate(AddressCreate):
    pass


class AddressResponse(AddressBase):
    """
    Docstring for AddressResponse
    id: integer id created by database
    client: client tied to the address
    """
    id: int

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

class ClientCreate(ClientBase):
    """
    Docstring for ClientCreate
    address_id: foreign key id mapped to an address
    """
    address_id: int
    phone_number: str = Field(max_length=15)
    email: EmailStr = Field(max_length=50)
    comment: Optional[str] = Field(max_length=750)
    

    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, number):
        """
        passes phone number to validator
        """
        return val.validate_phone_number(number)


        
class ClientUpdate(ClientBase):
    address_id: Optional[int] #TODO higher level check for valid address/create new address
    phone_number: Optional[str] = Field(max_length=15)
    email: Optional[EmailStr] = Field(max_length=50)
    comment: Optional[str] = Field(max_length = 750)

    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, num):
        if num is None:
            return num
        else: 
            return val.validate_phone_number(num)




class ClientResponse(ClientBase):
    """
    Docstring for ClientResponse
    address: address linked to client
    """
    id: int
    name: str
    address: AddressResponse


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
    status: BookingStatus = BookingStatus.SCHEDULED
    price: int #price in cents

    @field_validator('price')
    def validate_price(cls, price):
        """validates price is a non-zero postive integer

        Args:
            price (int): price of job

        Raises:
            ValueError: Price must be a non-zero postive integer

        Returns:
            int: price 
        """
        if price <= 1:
            raise ValueError("Price must be at least 1 cent")

        return price

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
    
    
class ConfirmedBookingUpdate(ConfirmedBookingBase):
    status: BookingStatus = BookingStatus.SCHEDULED
    assigned_employees: Optional[list[int]]
    price: Optional[int]

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
    
    @field_validator('price')
    def validate_price(cls, price):
        """validates price is a non-zero postive integer

        Args:
            price (int): price of job

        Raises:
            ValueError: Price must be a non-zero postive integer

        Returns:
            int: price 
        """
        if price <= 1:
            raise ValueError("Price must be at least 1 cent")

        return price

    

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

class BusinessInfoBase(BaseModel):
    business_name: str
    total_estimates: int

class BusinessInfoCreate(BusinessInfoBase):
    total_estimates: int

class BusinessInfoUpdate(BaseModel):
    business_name: Optional[str]
    total_estimates: Optional[int]

class BusinessInfoResponse(BusinessInfoBase):
    id: int

    class Config:
        from_attributes = True

class BusinessInfoDetailedResponse(BusinessInfoBase):
    id: int
    total_estimates: int
    business_name: str

    class Config:
        from_attributes = True

class BusinessInfoEstimateResponse(BusinessInfoBase):
    id: int
    total_estimates: int

    class Config:
        from_attributes = True


