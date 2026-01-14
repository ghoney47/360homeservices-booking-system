import phonenumbers as phone

#phone number validator
@staticmethod
def validate_phone_number(num):
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
    
#TODO zip code validator (check if valid in the us)

#TODO address validator (check if a servicable address)
