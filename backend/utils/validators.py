import re
import phonenumbers as phone
from phonenumbers import NumberParseException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Address, Client

# ── Constants ──────────────────────────────────────────────────────────────────

ZIP_RE = re.compile(r"^\d{5}$")

US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
    "DC",
}

VALID_JOB_TYPES = {"pwash", "gutter_cleaning"}

# ── Validators ─────────────────────────────────────────────────────────────────

@staticmethod
def validate_zip_code(zip_code: str) -> str:
    """Validates US zip code is exactly 5 digits."""
    if not ZIP_RE.match(zip_code):
        raise ValueError("Zip code must be exactly 5 digits (e.g. 98074)")
    return zip_code

@staticmethod
def validate_state(state: str) -> str:
    """Validates state is a recognised US state/territory abbreviation."""
    upper = state.upper()
    if upper not in US_STATES:
        raise ValueError(f"'{state}' is not a valid US state abbreviation")
    return upper

@staticmethod
def validate_job_type(job_type: str) -> str:
    """Validates job type is a known service."""
    if job_type not in VALID_JOB_TYPES:
        raise ValueError(
            f"Unknown job type '{job_type}'. Valid types: {', '.join(sorted(VALID_JOB_TYPES))}"
        )
    return job_type

#phone number validator
@staticmethod
def validate_phone_number(num):
    """
    Docstring for validate_phone_number

    :param num: string of the number input
    raise ValueError if invalid
    """
    default_region = "US"

    #parse phone number
    try:
        parsed_phone_num = phone.parse(num, default_region)
    except NumberParseException:
        raise ValueError("Invalid Phone Number") 
    except TypeError:
        raise ValueError("Invalid Phone Number")
    

    # checks valid phone number
    if phone.is_valid_number(parsed_phone_num):
        
        #converting to string
        normalized_num = phone.format_number(parsed_phone_num, phone.PhoneNumberFormat.E164)
        return normalized_num
    else:
        raise ValueError("Invalid Phone Number") 
    

#address exists check in database
@staticmethod
async def address_exists(address_id: int, db: AsyncSession) -> bool:
    stmt = select(Address).where(Address.id == address_id)
    result = await db.execute(stmt)
    address = result.scalar_one_or_none()

    if not address:
        return False
    
    return True

#client exists check in database
@staticmethod
async def client_exists(client_id: int, db: AsyncSession) -> bool:
    stmt = select(Client).where(Client.id == client_id)
    result = await db.execute(stmt)
    address = result.scalar_one_or_none()

    if not address:
        return False
    
    return True


    
#TODO zip code validator (check if valid in the us)

#TODO address validator (check if a servicable address)


