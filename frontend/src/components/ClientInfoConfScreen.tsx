import type { ClientForm } from './ClientInformation'

function ReviewRow({ label, value }: { label: string; value?: string }) {
  return (
    <div className="flex justify-between py-2 border-b border-gray-100 last:border-0">
      <span className="text-sm text-gray-500">{label}</span>
      <span className="text-sm font-medium text-gray-900 text-right max-w-xs">{value || '—'}</span>
    </div>
  )
}

const ClientInfoConfScreen = ({ formData }: { formData: ClientForm }) => {
  const address = `${formData.addrStNum} ${formData.addrStNam}, ${formData.addrCity}, ${formData.addrState} ${formData.addrZip}`

  return (
    <div className="max-w-xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Review</h1>
        <p className="text-gray-500 text-sm mt-1">Please confirm the information below before submitting.</p>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 space-y-5">
        <div>
          <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Name</h2>
          <ReviewRow label="Full Name" value={`${formData.fname} ${formData.lname}`} />
        </div>

        <div>
          <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Service Address</h2>
          <ReviewRow label="Address" value={address} />
        </div>

        <div>
          <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Contact</h2>
          <ReviewRow label="Phone" value={formData.phone} />
          <ReviewRow label="Email" value={formData.email} />
        </div>

        {formData.comment && (
          <div>
            <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Notes</h2>
            <ReviewRow label="Comment" value={formData.comment} />
          </div>
        )}
      </div>
    </div>
  )
}

export default ClientInfoConfScreen
