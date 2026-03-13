import { useState } from 'react'
interface ClientForm {
  fname: string;
  lname: string;
  email: string;
  address: string;
  phone: string;
  comment: string;
}

const initialFormState: ClientForm = {
  fname: " ",
  lname: " ",
  email: " ",
  address: " ",
  phone: " ",
  comment: " "
}

const ClientInformation = () => {
  const [formData, setForm] = useState<ClientForm>(initialFormState); 

  const handleTextChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const{ name, value } = e.target
    setForm((prev) => ({
      ...prev, 
      [name]: value
    }))
  }

  const handleSubmit = (e: React.SubmitEvent<HTMLFormElement>) => {
    e.preventDefault();
    console.log("Submitted data:", formData)
    //TODO: add API calls here and send to database
  }

  return (
    <form onSubmit = {handleSubmit}>

      <label htmlFor="fname">First Name:</label>
      <input id="fname" type = "text" name = "fname" value={formData.fname} 
      onChange={handleTextChange} placeholder='First Name'/> <br></br>

      <label htmlFor="lname">Last Name:</label>
      <input id='lname' type='text' name='lname' value={formData.lname} 
      onChange={handleTextChange} placeholder='Last Name'/> <br></br>

      <label htmlFor='email'>Email:</label>
      <input id='email' type= 'text' name='email' value={formData.email} 
      onChange={handleTextChange} placeholder='Email' /> <br></br>

      <label htmlFor='address'>Address:</label>
      <input id='address' type='text' name='address' value={formData.address}
      onChange={handleTextChange} placeholder='Address'/> <br></br>

      {/* should we add a checkbox for texting? do people even put land-lines here? */}
      <label htmlFor='phone'>Phone Number:</label>
      <input id='phone' type='text' name='phone' value={formData.phone}
      onChange={handleTextChange} placeholder='123-456-7890' /> <br></br>

      <label htmlFor='comment'>Additional Comments:</label>
      <input id='comment' type='text' name='comment' value={formData.comment}
      onChange={handleTextChange} placeholder='Comments'/> <br></br>

      <button type='submit'>Submit Form</button>
      
    </form>
  )
}

export default ClientInformation