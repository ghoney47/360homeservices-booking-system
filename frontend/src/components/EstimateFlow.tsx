import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

// ─── Scheduling config ────────────────────────────────────────────────────────
// TODO: replace with a config endpoint once business settings are built
const PW_DURATION_MINUTES = 120   //for pressure washing
const GC_DURATION_MINUTES = 120   //for gutter cleaning
const OP_START   = '08:00:00'
const OP_END     = '17:00:00'
const DEAD_START = '12:00:00'   // lunch window — no slots start here
const DEAD_END   = '13:00:00'
const SLOTS_PER_PAGE = 3
// ─────────────────────────────────────────────────────────────────────────────

type Step = 'estimate' | 'result' | 'book' | 'success'

interface AddressFields {
  stNum: string
  stNam: string
  city: string
  state: string
  zip: string
}

// Adds end-time and date strings to a raw ISO slot string
function parseSlot(iso: string, duration: number): { date: string; startTime: string; endTime: string; display: string } {
  const [datePart, timePart] = iso.split('T')
  const [year, month, day] = datePart.split('-').map(Number)
  const [h, m] = timePart.split(':').map(Number)

  const jsDate = new Date(year, month - 1, day)
  const dayName   = jsDate.toLocaleDateString('en-US', { weekday: 'short' })
  const monthName = jsDate.toLocaleDateString('en-US', { month: 'short' })
  const ampm        = h >= 12 ? 'PM' : 'AM'
  const displayHour = h > 12 ? h - 12 : h === 0 ? 12 : h
  const displayMin  = m.toString().padStart(2, '0')

  const totalEndMins = h * 60 + m + duration
  const endH = Math.floor(totalEndMins / 60).toString().padStart(2, '0')
  const endM = (totalEndMins % 60).toString().padStart(2, '0')

  return {
    date: datePart,
    startTime: timePart,
    endTime: `${endH}:${endM}:00`,
    display: `${dayName}, ${monthName} ${day}  ·  ${displayHour}:${displayMin} ${ampm}`,
  }
}

function SectionLabel({ children }: { children: string }) {
  return (
    <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
      {children}
    </p>
  )
}

function Field({
  label, id, name, value, onChange, placeholder, type = 'text', required, className = '',
}: {
  label: string; id: string; name: string; value: string
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void
  placeholder?: string; type?: string; required?: boolean; className?: string
}) {
  return (
    <div className={`flex flex-col gap-1 ${className}`}>
      <label htmlFor={id} className="text-sm font-medium text-gray-700">
        {label}{required && <span className="text-red-500 ml-0.5">*</span>}
      </label>
      <input
        id={id} type={type} name={name} value={value} onChange={onChange}
        placeholder={placeholder} required={required}
        className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none
                   focus:ring-2 focus:ring-green-500 focus:border-transparent placeholder-gray-400"
      />
    </div>
  )
}

// ─── Screen 1: Estimate form ──────────────────────────────────────────────────
function EstimateScreen({
  address, setAddress, jobType, setJobType, sqFt, setSqFt,
  onSubmit, error, isLoading,
}: {
  address: AddressFields
  setAddress: (a: AddressFields) => void
  jobType: string
  setJobType: (j: string) => void
  sqFt: string
  setSqFt: (s: string) => void
  onSubmit: () => void
  error: string
  isLoading: boolean
}) {
  const handleAddr = (e: React.ChangeEvent<HTMLInputElement>) =>
    setAddress({ ...address, [e.target.name]: e.target.value })

  return (
    <div className="max-w-xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Home Services Estimator</h1>
        <p className="text-gray-500 text-sm mt-1">Enter your address to get an instant price estimate.</p>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 space-y-6">

        {/* Address */}
        <div>
          <SectionLabel>Service Address</SectionLabel>
          <div className="space-y-3">
            <div className="grid grid-cols-3 gap-3">
              <Field label="Street #" id="stNum" name="stNum" value={address.stNum}
                onChange={handleAddr} placeholder="123" required />
              <Field label="Street Name" id="stNam" name="stNam" value={address.stNam}
                onChange={handleAddr} placeholder="Maple Ave" required className="col-span-2" />
            </div>
            <div className="grid grid-cols-3 gap-3">
              <Field label="City" id="city" name="city" value={address.city}
                onChange={handleAddr} placeholder="Springfield" required />
              <Field label="State" id="state" name="state" value={address.state}
                onChange={handleAddr} placeholder="IL" required />
              <Field label="Zip" id="zip" name="zip" value={address.zip}
                onChange={handleAddr} placeholder="62701" required />
            </div>
          </div>
        </div>

        {/* Service Details — placeholder banner */}
        <div>
          <SectionLabel>Service Details</SectionLabel>

          <div className="mb-3 flex items-start gap-2 bg-amber-50 border border-amber-200
                          rounded-lg px-3 py-2 text-xs text-amber-800">
            <span className="mt-0.5 text-amber-500 font-bold">⚠</span>
            <span>
              <strong>Placeholder — pricing method not yet finalized.</strong>{' '}
              These inputs will change before production. Do not use for official quotes.
            </span>
          </div>

          <div className="space-y-3">
            <div className="flex flex-col gap-1">
              <label htmlFor="jobType" className="text-sm font-medium text-gray-700">
                Service Type<span className="text-red-500 ml-0.5">*</span>
              </label>
              <select
                id="jobType"
                value={jobType}
                onChange={(e) => setJobType(e.target.value)}
                className="border border-gray-300 rounded-md px-3 py-2 text-sm
                           focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent
                           bg-white text-gray-700"
              >
                <option value="">Select a service…</option>
                <option value="pwash">Pressure Washing</option>
                <option value="gutter_cleaning" disabled>
                  Gutter Cleaning (estimator coming soon)
                </option>
              </select>
            </div>

            {jobType === 'pwash' && (
              <Field
                label="Approximate Square Footage (placeholder)"
                id="sqFt" name="sqFt" value={sqFt}
                onChange={(e) => setSqFt(e.target.value)}
                placeholder="e.g. 1200"
                type="number"
                required
              />
            )}
          </div>
        </div>

        {error && <p className="text-red-500 text-sm">{error}</p>}

        <button
          onClick={onSubmit}
          disabled={isLoading}
          className="w-full bg-green-700 text-white py-2 rounded-md text-sm font-medium
                     hover:bg-green-800 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Calculating…' : 'Get Estimate →'}
        </button>
      </div>
    </div>
  )
}

// ─── Screen 2: Estimate result ────────────────────────────────────────────────
function ResultScreen({
  address, jobType, priceDisplay, onBookNow, onSaveForLater,
}: {
  address: string; jobType: string; priceDisplay: string
  onBookNow: () => void; onSaveForLater: () => void
}) {
  const jobLabel = jobType === 'pwash' ? 'Pressure Washing' : 'Gutter Cleaning'

  return (
    <div className="max-w-xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Your Estimate</h1>
        <p className="text-gray-500 text-sm mt-1">
          At <span className="font-medium text-gray-700">{address}</span> for{' '}
          <span className="font-medium text-gray-700">{jobLabel}</span>, we estimate the cost to be:
        </p>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 space-y-6">
        {/* Price box */}
        <div className="border-2 border-green-500 rounded-xl py-8 text-center">
          <p className="text-4xl font-bold text-green-700">{priceDisplay}</p>
          <p className="text-xs text-gray-400 mt-2">Estimated price · subject to on-site review</p>
        </div>

        {/* Actions */}
        <button
          onClick={onBookNow}
          className="w-full bg-green-700 text-white py-3 rounded-md font-semibold
                     hover:bg-green-800 transition-colors"
        >
          Book Now
        </button>

        <div className="relative flex items-center">
          <div className="flex-1 border-t border-dashed border-gray-300" />
          <span className="mx-3 text-xs text-gray-400">or</span>
          <div className="flex-1 border-t border-dashed border-gray-300" />
        </div>

        <button
          onClick={onSaveForLater}
          className="w-full border border-dashed border-gray-300 text-gray-500 py-2 rounded-md
                     text-sm hover:bg-gray-50 transition-colors"
        >
          Save for later — leave your contact info
        </button>
      </div>
    </div>
  )
}

// ─── Screen 3: Booking form ───────────────────────────────────────────────────
function BookingScreen({
  slots, slotsLoading, slotsError,
  selectedSlot, setSelectedSlot,
  userName, setUserName,
  userPhone, setUserPhone,
  userEmail, setUserEmail,
  onBook, onBack, isLoading, error, jobDuration,
}: {
  slots: string[]; slotsLoading: boolean; slotsError: string
  selectedSlot: string | null; setSelectedSlot: (s: string) => void
  userName: string; setUserName: (s: string) => void
  userPhone: string; setUserPhone: (s: string) => void
  userEmail: string; setUserEmail: (s: string) => void
  onBook: () => void; onBack: () => void; isLoading: boolean; error: string; jobDuration: number
}) {
  const [page, setPage] = useState(0)
  const totalPages = Math.ceil(slots.length / SLOTS_PER_PAGE)
  const visible = slots.slice(page * SLOTS_PER_PAGE, page * SLOTS_PER_PAGE + SLOTS_PER_PAGE)

  return (
    <div className="max-w-xl mx-auto space-y-4">
      <div className="mb-6">
        <button
          onClick={onBack}
          className="flex items-center gap-1 text-sm text-green-700 hover:text-green-900 mb-3 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to estimate
        </button>
        <h1 className="text-2xl font-bold text-gray-900">Book Your Appointment</h1>
        <p className="text-gray-500 text-sm mt-1">Choose a time and enter your contact info.</p>
      </div>

      {/* User info */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 space-y-4">
        <SectionLabel>Your Information</SectionLabel>
        <Field label="Full Name" id="userName" name="userName" value={userName}
          onChange={(e) => setUserName(e.target.value)} placeholder="Jane Smith" required />
        <Field label="Phone" id="userPhone" name="userPhone" value={userPhone}
          onChange={(e) => setUserPhone(e.target.value)} placeholder="123-456-7890" type="tel" required />
        <Field label="Email" id="userEmail" name="userEmail" value={userEmail}
          onChange={(e) => setUserEmail(e.target.value)} placeholder="jane@example.com" type="email" required />
      </div>

      {/* Time slot picker */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
        <SectionLabel>Available Times</SectionLabel>

        {slotsLoading && (
          <p className="text-sm text-gray-400 text-center py-4">Loading available times…</p>
        )}

        {slotsError && !slotsLoading && (
          <p className="text-sm text-red-500 text-center py-4">{slotsError}</p>
        )}

        {!slotsLoading && !slotsError && slots.length === 0 && (
          <p className="text-sm text-gray-400 text-center py-4">No available slots found.</p>
        )}

        {!slotsLoading && slots.length > 0 && (
          <>
            <div className="grid grid-cols-3 gap-3 mb-4">
              {visible.map((iso) => {
                const { display } = parseSlot(iso, jobDuration)
                const isSelected = selectedSlot === iso
                return (
                  <button
                    key={iso}
                    onClick={() => setSelectedSlot(iso)}
                    className={`text-xs text-center px-2 py-3 rounded-lg border transition-colors leading-snug
                      ${isSelected
                        ? 'bg-green-700 text-white border-green-700 font-semibold'
                        : 'border-gray-200 text-gray-700 hover:border-green-400 hover:bg-green-50'
                      }`}
                  >
                    {display.split('  ·  ').map((part, i) => (
                      <span key={i} className="block">{part}</span>
                    ))}
                  </button>
                )
              })}
            </div>

            {/* Pagination */}
            <div className="flex items-center justify-between">
              <button
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                disabled={page === 0}
                className="text-sm text-gray-500 hover:text-gray-800 disabled:opacity-30 transition-opacity"
              >
                ← Earlier
              </button>
              <span className="text-xs text-gray-400">
                {page + 1} / {totalPages}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                disabled={page >= totalPages - 1}
                className="text-sm text-gray-500 hover:text-gray-800 disabled:opacity-30 transition-opacity"
              >
                Later →
              </button>
            </div>
          </>
        )}
      </div>

      {error && <p className="text-red-500 text-sm">{error}</p>}

      <button
        onClick={onBook}
        disabled={isLoading || !selectedSlot || !userName || !userPhone || !userEmail}
        className="w-full bg-green-700 text-white py-3 rounded-md font-semibold
                   hover:bg-green-800 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
      >
        {isLoading ? 'Booking…' : 'Book Now'}
      </button>
      <p className="text-center text-xs text-gray-400">Contact info required to confirm your booking.</p>
    </div>
  )
}

// ─── Root component ───────────────────────────────────────────────────────────
export default function EstimateFlow() {
  const navigate = useNavigate()

  const [step, setStep] = useState<Step>('estimate')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError]   = useState('')

  // Screen 1
  const [address, setAddress] = useState<AddressFields>({ stNum: '', stNam: '', city: '', state: '', zip: '' })
  const [jobType, setJobType] = useState('')
  const [sqFt, setSqFt]       = useState('')

  // Screen 2
  const [priceDisplay, setPriceDisplay]   = useState('')
  const [priceCents, setPriceCents]       = useState(0)
  const [estimatedAddress, setEstimatedAddress] = useState('')

  // Screen 3
  const [slots, setSlots]               = useState<string[]>([])
  const [slotsLoading, setSlotsLoading] = useState(false)
  const [slotsError, setSlotsError]     = useState('')
  const [selectedSlot, setSelectedSlot] = useState<string | null>(null)
  const [userName, setUserName]         = useState('')
  const [userPhone, setUserPhone]       = useState('')
  const [userEmail, setUserEmail]       = useState('')

  // ── Screen 1: get estimate ─────────────────────────────────────
  const handleGetEstimate = async () => {
    const { stNum, stNam, city, state, zip } = address
    if (!stNum || !stNam || !city || !state || !zip || !jobType) {
      setError('Please fill in all required fields.'); return
    }
    if (jobType === 'pwash' && !sqFt) {
      setError('Please enter the square footage.'); return
    }

    setError(''); setIsLoading(true)

    try {
      const res = await fetch('/api/v1/services/estimate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          street_number: stNum,
          street_name: stNam,
          city,
          state,
          zip_code: zip,
          job_type: jobType,
          sq_ft: sqFt ? parseFloat(sqFt) : null,
        }),
      })
      if (!res.ok) {
        let detail = `Server error ${res.status}`
        try { detail = (await res.json()).detail ?? detail } catch { /* non-JSON proxy error */ }
        throw new Error(detail)
      }
      const data = await res.json()
      setPriceDisplay(data.estimated_price_display)
      setPriceCents(data.estimated_price_cents)
      setEstimatedAddress(data.address)
      setStep('result')
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Something went wrong.')
    } finally {
      setIsLoading(false)
    }
  }


  //selecting estimated duration based on job type
  const jobDuration = jobType === 'pwash' ? PW_DURATION_MINUTES : GC_DURATION_MINUTES

  // ── Screen 2 → 3: load available slots ────────────────────────
  const handleGoToBook = async () => {
    setStep('book')
    setSlotsLoading(true); setSlotsError('')

    try {
      const today = new Date().toISOString().split('T')[0]
      const params = new URLSearchParams({
        duration:    String(jobDuration),
        start_date:  today,
        op_start:    OP_START,
        op_end:      OP_END,
        dead_start:  DEAD_START,
        dead_end:    DEAD_END,
      })
      const res = await fetch(`/api/v1/bookings/openings?${params}`)
      if (!res.ok) throw new Error(`Failed to load slots (${res.status})`)
      setSlots(await res.json())
    } catch (err: unknown) {
      setSlotsError(err instanceof Error ? err.message : 'Could not load available times.')
    } finally {
      setSlotsLoading(false)
    }
  }

  // ── Screen 3: create booking ───────────────────────────────────
  const handleBook = async () => {
    if (!selectedSlot) return
    setError(''); setIsLoading(true)

    const { date: slotDate, startTime, endTime } = parseSlot(selectedSlot, jobDuration)

    try {
      // 1. Create address
      const addrRes = await fetch('/api/v1/addresses/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          street_number: address.stNum,
          street_name:   address.stNam,
          city:          address.city,
          state:         address.state,
          zip_code:      address.zip,
        }),
      })
      if (!addrRes.ok) throw new Error(`Address error: ${addrRes.status}`)
      const newAddr = await addrRes.json()

      // 2. Create client
      const clientRes = await fetch('/api/v1/clients/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name:         userName,
          address_id:   newAddr.id,
          phone_number: userPhone,
          email:        userEmail,
        }),
      })
      if (!clientRes.ok) throw new Error(`Client error: ${clientRes.status}`)
      const newClient = await clientRes.json()

      // 3. Create booking
      // TODO: replace job_id=1 with a real job ID once job management is built
      const bookRes = await fetch('/api/v1/bookings/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          job_id:             1,
          address_id:         newAddr.id,
          client_id:          newClient.id,
          date:               slotDate,
          start_time:         startTime,
          end_time:           endTime,
          status:             'scheduled',
          price:              priceCents,
          assigned_employees: [],
        }),
      })
      if (!bookRes.ok) throw new Error(`Booking error: ${bookRes.status}`)

      setStep('success')
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Something went wrong. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  // ── Success screen ─────────────────────────────────────────────
  if (step === 'success') {
    return (
      <div className="max-w-xl mx-auto mt-16 text-center">
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-10">
          <div className="w-14 h-14 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-7 h-7 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Booking Confirmed</h2>
          <p className="text-gray-500 text-sm mb-6">
            We've got you on the schedule. We'll be in touch to confirm the details.
          </p>
          <button
            onClick={() => { setStep('estimate'); setAddress({ stNum:'',stNam:'',city:'',state:'',zip:'' }); setJobType(''); setSqFt(''); setSelectedSlot(null) }}
            className="bg-green-700 text-white px-6 py-2 rounded-md text-sm font-medium hover:bg-green-800 transition-colors"
          >
            New Estimate
          </button>
        </div>
      </div>
    )
  }

  return (
    <>
      {step === 'estimate' && (
        <EstimateScreen
          address={address} setAddress={setAddress}
          jobType={jobType} setJobType={setJobType}
          sqFt={sqFt} setSqFt={setSqFt}
          onSubmit={handleGetEstimate} error={error} isLoading={isLoading}
        />
      )}

      {step === 'result' && (
        <ResultScreen
          address={estimatedAddress} jobType={jobType} priceDisplay={priceDisplay}
          onBookNow={handleGoToBook}
          onSaveForLater={() =>
            navigate('/clients/new', {
              state: {
                fromEstimate: true,
                prefilledAddress: {
                  addrStNum: address.stNum,
                  addrStNam: address.stNam,
                  addrCity:  address.city,
                  addrState: address.state,
                  addrZip:   address.zip,
                },
              },
            })
          }
        />
      )}

      {step === 'book' && (
        <BookingScreen
          slots={slots} slotsLoading={slotsLoading} slotsError={slotsError}
          selectedSlot={selectedSlot} setSelectedSlot={setSelectedSlot}
          userName={userName} setUserName={setUserName}
          userPhone={userPhone} setUserPhone={setUserPhone}
          userEmail={userEmail} setUserEmail={setUserEmail}
          onBook={handleBook} onBack={() => setStep('result')} isLoading={isLoading} error={error} jobDuration={jobDuration}
        />
      )}
    </>
  )
}
