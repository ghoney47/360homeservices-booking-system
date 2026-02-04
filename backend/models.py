import database as db
import enum as en
import sqlalchemy as sa
from sqlalchemy import Table, Column, ForeignKey
import datetime as dt
from sqlalchemy.orm import Mapped, mapped_column, relationship

# pulls base from database
Base = db.Base
metadata = Base.metadata

#TODO check syntax overall
#TODO better comments/documentation 

class BusinessInfo(Base):
    __tablename__ = "business information"
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=False)
    total_estimates: Mapped[int]
    business_name: Mapped[str] = mapped_column(sa.String(70))

assigned_jobs = Table (
    "assigned_jobs",
    metadata,
    Column("booking_id", ForeignKey("confirmed_bookings.id_hash"), primary_key=True),
    Column("employee_id", ForeignKey("employees.id"), primary_key=True),
    comment="<stores employees and the jobs they are assigned to>"
)


class Employee(Base):
    """
    defines table that stores employee ids for assignment
    """
    __tablename__ = "employees"
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True, autoincrement=True, nullable=False)
    name: Mapped[str] = mapped_column(sa.String(50), unique=True, nullable=False) 
    phone_number: Mapped[str] = mapped_column(sa.String(15), unique=True, nullable=False) #includes country code
    email: Mapped[str] = mapped_column(sa.String(50), nullable=True, unique=True)
    created_at: Mapped[dt.datetime] = mapped_column(sa.DateTime, server_default=sa.func.now(), nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now(), nullable = True)
    hire_date: Mapped[dt.datetime] = mapped_column(sa.Date) 
    assigned_jobs: Mapped[list["ConfirmedBooking"]] = relationship(secondary=assigned_jobs, back_populates="assigned_employees")


    def __repr__(self) -> str:
        return f"<Employee: {self.name}\nID: {self.id}\nContact info: email = {self.email}, phone = {self.phone_number}>"
    

class Job (Base):
    """
    defines table that stores each job (service) type
    """
    __tablename__ = "jobs"
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, unique=True, index=True, autoincrement=True)
    title: Mapped[str] = mapped_column(sa.String(20), unique = True)

    def __repr__(self) -> str:
        return f"<The service {self.title} is mapped to {self.id}>"

class BookingStatus(en.Enum):
    COMPLETED = "completed"
    IN_PROCESS = "in_process"
    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"


class ConfirmedBooking (Base): 
    """
    Stores information for a given booking
    """
    __tablename__ = "confirmed_bookings"

    id_hash: Mapped[str] = mapped_column(sa.String, primary_key=True, unique=True, nullable=False) # TODO: when creating the object, hash the object 
    job_id: Mapped[int] = mapped_column(nullable=False)

    address_id: Mapped[int] = mapped_column(ForeignKey("addresses.id"), nullable=False)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)

    address: Mapped["Address"] = relationship(back_populates="confirmed_bookings")
    client: Mapped["Client"] = relationship(back_populates="confirmed_bookings")

    assigned_employees: Mapped[list["Employee"]] = relationship(secondary=assigned_jobs, back_populates="assigned_jobs")

    date: Mapped[dt.date] = mapped_column(sa.Date)
    start_time: Mapped[dt.time] = mapped_column(sa.Time)
    end_time: Mapped[dt.time] = mapped_column(sa.Time)
    status: Mapped["BookingStatus"] = mapped_column(sa.Enum(BookingStatus), nullable = False)
    created_at: Mapped[dt.datetime] = mapped_column(sa.DateTime, server_default=sa.func.now(), nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now(), nullable = True)
    price: Mapped[int] = mapped_column(sa.Integer) #price in cents
    def __repr__(self) -> str:
        return f"<Booking {self.id_hash} to be completed at {self.address}\nStart time: {self.start_time} and ending at {self.end_time}\nJob Status: {self.status}>"



    


class Address(Base):
    """
    Stores address information, and jobs that have been completed at that address
    """
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, unique=True, autoincrement=True, nullable = False)
    street_number: Mapped[str] = mapped_column(sa.String(10), nullable = False) 
    street_name: Mapped[str] = mapped_column(sa.String(50), nullable = False)
    city: Mapped[str] = mapped_column(sa.String(20), nullable = False)
    state: Mapped[str] = mapped_column(sa.String(2), nullable = False) # State abreviation 
    zip_code: Mapped[str] = mapped_column(sa.String(5), nullable = False) #TODO: this and country to check if out of service range

    client: Mapped["Client"] = relationship(back_populates="address", uselist=False)

    confirmed_bookings: Mapped[list["ConfirmedBooking"]] = relationship(back_populates="address")

    def __repr__ (self) -> str:
        return f"<At {self.street_number} {self.street_name} {self.city}, {self.state} {self.zip_code}>"


class Client(Base):
    """
    Stores client information
    """

    __tablename__ = "clients"
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, unique=True, autoincrement=True, index=True, nullable = False)

    address_id: Mapped[int] = mapped_column(ForeignKey("addresses.id"), unique=True, nullable=False)
    address: Mapped["Address"] = relationship(back_populates = "client") 

    name: Mapped[str] = mapped_column(sa.String(50), unique=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(sa.String(15), unique=True, nullable=False) #includes country code
    email: Mapped[str] = mapped_column(sa.String(50), nullable=True, unique=True) 
    comment: Mapped[str] = mapped_column(sa.String(750), nullable=True) #for a comment box


    confirmed_bookings: Mapped[list["ConfirmedBooking"]] = relationship(back_populates="client") 

    def __repr__(self) -> str:
        return f"<Client {self.name}, id = {self.id} resides at {self.address}\nPhone: {self.phone_number} Email: {self.email}>"
    




