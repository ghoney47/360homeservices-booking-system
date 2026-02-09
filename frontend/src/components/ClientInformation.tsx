import { useState } from 'react'

const ClientInformation = () => {
  const [fName, setFName] = useState(" ");
  const [lName, setLName] = useState(" ");
  const [email, setEmail] = useState(" ");
  const [address, setAddress] = useState(" ");
  const [phone, setPhone] = useState(" ");
  const [comment, setComment] = useState(" ");



  return (
    <>
    <label>
      First Name: 
      <input 
      defaultValue="Enter First Name" 
      value={fName}
      onChange={e => setFName(e.target.value)}
      />
    </label>
    
    </>
  )
}

export default ClientInformation