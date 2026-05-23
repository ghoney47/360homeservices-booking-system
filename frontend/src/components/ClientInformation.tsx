import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import ClientInfoConfScreen from './ClientInfoConfScreen'

export interface ClientForm {
  fname: string
  lname: string
  email: string
  addrStNum: string
  addrStNam: string
  addrCity: string
  addrState: string
  addrZip: string
  phone: string
  comment?: string
}

const initialFormState: ClientForm = {
  fname: '',
  lname: '',
  email: '',
  addrStNum: '',
  addrStNam: '',
  addrCity: '',
  addrState: '',
  addrZip: '',
  phone: '',
  comment: '',
}

function FormField({
  label,
  id,
  name,
  value,
  onChange,
  placeholder,
  required,
  type = 'text',
  className = '',
}: {
  label: string
  id: string
  name: string
  value: string
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void
  placeholder?: string
  required?: boolean
  type?: string
  className?: string
}) {
  return (
    <div className={`flex flex-col gap-1 ${className}`}>
      <label htmlFor={id} className="text-sm font-medium text-gray-700">
        {label}
        {required && <span className="text-red-500 ml-0.5">*</span>}
      </label>
      <input
        id={id}
        type={type}
        name={name}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        required={required}
        className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent placeholder-gray-400"
      />
    </div>
  )
}

const ClientInformation = () => {
  const location = useLocation()
  const navigate  = useNavigate()
  const locationState = location.state as { fromEstimate?: boolean; prefilledAddress?: Partial<ClientForm> } | null

  const [step, setStep] = useState<'form' | 'review' | 'success' | 'error'>('form')
  const [formData, setForm] = useState<ClientForm>({
    ...initialFormState,
    ...(locationState?.prefilledAddress ?? {}),
  })
  const [error, setError] = useState<string>('')
  const [isLoading, setIsLoading] = useState<boolean>(false)

  const handleTextChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setForm((prev) => ({ ...prev, [name]: value }))
  }

  const handleReview = () => {
    const { fname, lname, phone, email, addrStNum, addrStNam, addrCity, addrState, addrZip } = formData
    if (!fname || !lname || !phone || !email || !addrStNum || !addrStNam || !addrCity || !addrState || !addrZip) {
      setError('Please fill in all required fields.')
      setStep('error')
      return
    }
    setError('')
    setStep('review')
  }

  const handleSubmit = async () => {
    setError('')
    setIsLoading(true)

    const { fname, lname, email, addrStNum, addrStNam, addrCity, addrState, addrZip, phone, comment } = formData
    const name = `${fname} ${lname}`
    const address = `${addrStNum} ${addrStNam} ${addrCity}, ${addrState} ${addrZip}`

    try {
      // Fire-and-forget: sync to Homebase360 CRM (temporary — will be replaced by proprietary CMS).
      // Failures are logged but do NOT block the local record creation.
      fetch('https://us-central1-homebase-360.cloudfunctions.net/api/v1/customers', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          firstName: fname,
          lastName: lname,
          phone: { mobile: phone },
          email: [email],
          address: [address],
          notes: comment,
          notifications: true,
        }),
      }).then((r) => {
        if (!r.ok) console.warn('Homebase360 sync failed:', r.status)
      }).catch((e) => console.warn('Homebase360 sync error:', e))

      // Create address record
      const addressResponse = await fetch('/api/v1/addresses/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          street_number: addrStNum,
          street_name: addrStNam,
          city: addrCity,
          state: addrState,
          zip_code: addrZip,
        }),
      })

      if (!addressResponse.ok) throw new Error(`Address API error: ${addressResponse.status}`)
      const newAddress = await addressResponse.json()

      // Create client record
      const clientResponse = await fetch('/api/v1/clients/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          address_id: newAddress.id,
          phone_number: phone,
          email,
          comment,
        }),
      })

      if (!clientResponse.ok) throw new Error(`Client API error: ${clientResponse.status}`)

      setStep('success')
    } catch (err) {
      setError('Something went wrong. Please try again.')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  if (step === 'success') {
    return (
      <div className="max-w-xl mx-auto mt-16 text-center">
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-10">
          <div className="w-14 h-14 bg-brand-light rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-7 h-7 text-brand" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Client Added</h2>
          <p className="text-gray-500 text-sm mb-6">The client information has been saved successfully.</p>
          <button
            onClick={() => { setForm(initialFormState); setStep('form') }}
            className="bg-brand text-white px-6 py-2 rounded-md text-sm font-medium hover:bg-brand-dark transition-colors"
          >
            Add Another Client
          </button>
        </div>
      </div>
    )
  }

  if (step === 'error') {
    return (
      <div className="max-w-xl mx-auto mt-16 text-center">
        <div className="bg-white rounded-2xl shadow-sm border border-red-100 p-10">
          <div className="w-14 h-14 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-7 h-7 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Missing Information</h2>
          <p className="text-red-500 text-sm mb-6">{error}</p>
          <button
            onClick={() => setStep('form')}
            className="bg-brand text-white px-6 py-2 rounded-md text-sm font-medium hover:bg-brand-dark transition-colors"
          >
            Go Back
          </button>
        </div>
      </div>
    )
  }

  if (step === 'review') {
    return (
      <>
        <ClientInfoConfScreen formData={formData} />
        <div className="max-w-xl mx-auto flex gap-3 mt-4">
          <button
            onClick={() => setStep('form')}
            className="flex-1 border border-gray-300 text-gray-700 px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-50 transition-colors"
          >
            Back
          </button>
          <button
            onClick={handleSubmit}
            disabled={isLoading}
            className="flex-1 bg-brand text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-brand-dark transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Submitting…' : 'Confirm & Submit'}
          </button>
        </div>
      </>
    )
  }

  return (
    <div className="max-w-xl mx-auto">
      <div className="mb-6">
        {locationState?.fromEstimate && (
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-1 text-sm text-brand hover:text-brand-dark mb-3 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to estimate
          </button>
        )}
        <h1 className="text-2xl font-bold text-gray-900">New Client</h1>
        <p className="text-gray-500 text-sm mt-1">Enter the client's contact and address information.</p>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 space-y-6">
        {/* Name */}
        <div>
          <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Name</h2>
          <div className="grid grid-cols-2 gap-3">
            <FormField label="First Name" id="fname" name="fname" value={formData.fname} onChange={handleTextChange} placeholder="Jane" required />
            <FormField label="Last Name" id="lname" name="lname" value={formData.lname} onChange={handleTextChange} placeholder="Smith" required />
          </div>
        </div>

        {/* Address */}
        <div>
          <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Service Address</h2>
          <div className="space-y-3">
            <div className="grid grid-cols-3 gap-3">
              <FormField label="Street #" id="addrStNum" name="addrStNum" value={formData.addrStNum} onChange={handleTextChange} placeholder="123" required />
              <FormField label="Street Name" id="addrStNam" name="addrStNam" value={formData.addrStNam} onChange={handleTextChange} placeholder="Maple Ave" required className="col-span-2" />
            </div>
            <div className="grid grid-cols-3 gap-3">
              <FormField label="City" id="addrCity" name="addrCity" value={formData.addrCity} onChange={handleTextChange} placeholder="Springfield" required className="col-span-1" />
              <FormField label="State" id="addrState" name="addrState" value={formData.addrState} onChange={handleTextChange} placeholder="IL" required />
              <FormField label="Zip Code" id="addrZip" name="addrZip" value={formData.addrZip} onChange={handleTextChange} placeholder="62701" required />
            </div>
          </div>
        </div>

        {/* Contact */}
        <div>
          <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Contact</h2>
          <div className="space-y-3">
            <FormField label="Phone Number" id="phone" name="phone" value={formData.phone} onChange={handleTextChange} placeholder="123-456-7890" required type="tel" />
            <FormField label="Email" id="email" name="email" value={formData.email} onChange={handleTextChange} placeholder="jane@example.com" required type="email" />
          </div>
        </div>

        {/* Comments */}
        <div>
          <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Notes</h2>
          <div className="flex flex-col gap-1">
            <label htmlFor="comment" className="text-sm font-medium text-gray-700">How did you hear about us?</label>
            <input
              id="comment"
              type="text"
              name="comment"
              value={formData.comment}
              onChange={handleTextChange}
              placeholder="Online, Word-of-mouth, etc"
              className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent placeholder-gray-400"
            />
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3 pt-2">
          <button
            type="reset"
            onClick={() => setForm(initialFormState)}
            className="border border-gray-300 text-gray-700 px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-50 transition-colors"
          >
            Clear
          </button>
          <button
            type="button"
            onClick={handleReview}
            className="flex-1 bg-brand text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-brand-dark transition-colors"
          >
            Review
          </button>
        </div>
      </div>
    </div>
  )
}

export default ClientInformation
