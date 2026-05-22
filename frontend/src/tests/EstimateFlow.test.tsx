import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import EstimateFlow from '../components/EstimateFlow'

// ── Helpers ────────────────────────────────────────────────────────────────────

function renderFlow() {
  return render(
    <MemoryRouter>
      <EstimateFlow />
    </MemoryRouter>
  )
}

function mockFetch(responses: Record<string, unknown>) {
  return vi.fn((url: string) => {
    const key = Object.keys(responses).find((k) => url.includes(k))
    const body = key ? responses[key] : {}
    return Promise.resolve({
      ok: true,
      status: 200,
      json: () => Promise.resolve(body),
    })
  })
}

// ── Screen 1: Estimate form ────────────────────────────────────────────────────

describe('EstimateFlow — estimate form (screen 1)', () => {
  it('renders the estimate form on load', () => {
    renderFlow()
    expect(screen.getByText('Home Services Estimator')).toBeInTheDocument()
    expect(screen.getByText('Get Estimate →')).toBeInTheDocument()
  })

  it('shows an error if required fields are empty on submit', async () => {
    renderFlow()
    await userEvent.click(screen.getByText('Get Estimate →'))
    expect(screen.getByText('Please fill in all required fields.')).toBeInTheDocument()
  })

  it('shows sq ft field only when Pressure Washing is selected', async () => {
    renderFlow()
    expect(screen.queryByLabelText(/square footage/i)).not.toBeInTheDocument()
    await userEvent.selectOptions(screen.getByRole('combobox'), 'pwash')
    expect(screen.getByLabelText(/square footage/i)).toBeInTheDocument()
  })

  it('shows sq ft error when job is pwash but sq ft is empty', async () => {
    renderFlow()
    await userEvent.selectOptions(screen.getByRole('combobox'), 'pwash')
    // Fill address but not sq ft
    await userEvent.type(screen.getByPlaceholderText('123'), '123')
    await userEvent.type(screen.getByPlaceholderText('Maple Ave'), 'Maple Ave')
    await userEvent.type(screen.getByPlaceholderText('Springfield'), 'Springfield')
    await userEvent.type(screen.getByPlaceholderText('IL'), 'IL')
    await userEvent.type(screen.getByPlaceholderText('62701'), '62701')
    await userEvent.click(screen.getByText('Get Estimate →'))
    expect(screen.getByText('Please enter the square footage.')).toBeInTheDocument()
  })

  it('calls /api/v1/services/estimate and advances to result screen', async () => {
    global.fetch = mockFetch({
      '/api/v1/services/estimate': {
        estimated_price_display: '$150.00',
        estimated_price_cents: 15000,
        address: '123 Maple Ave, Springfield, IL 62701',
      },
    }) as typeof fetch

    renderFlow()
    await userEvent.selectOptions(screen.getByRole('combobox'), 'pwash')
    await userEvent.type(screen.getByPlaceholderText('123'), '123')
    await userEvent.type(screen.getByPlaceholderText('Maple Ave'), 'Maple Ave')
    await userEvent.type(screen.getByPlaceholderText('Springfield'), 'Springfield')
    await userEvent.type(screen.getByPlaceholderText('IL'), 'IL')
    await userEvent.type(screen.getByPlaceholderText('62701'), '62701')
    await userEvent.type(screen.getByPlaceholderText('e.g. 1200'), '1200')
    await userEvent.click(screen.getByText('Get Estimate →'))

    await waitFor(() => expect(screen.getByText('Your Estimate')).toBeInTheDocument())
    expect(screen.getByText('$150.00')).toBeInTheDocument()
  })
})

// ── Screen 2: Result ───────────────────────────────────────────────────────────

describe('EstimateFlow — result screen (screen 2)', () => {
  async function advanceToResult() {
    global.fetch = mockFetch({
      '/api/v1/services/estimate': {
        estimated_price_display: '$150.00',
        estimated_price_cents: 15000,
        address: '123 Maple Ave, Springfield, IL 62701',
      },
      '/api/v1/intake/openings': [],
    }) as typeof fetch

    renderFlow()
    await userEvent.selectOptions(screen.getByRole('combobox'), 'pwash')
    await userEvent.type(screen.getByPlaceholderText('123'), '123')
    await userEvent.type(screen.getByPlaceholderText('Maple Ave'), 'Maple Ave')
    await userEvent.type(screen.getByPlaceholderText('Springfield'), 'Springfield')
    await userEvent.type(screen.getByPlaceholderText('IL'), 'IL')
    await userEvent.type(screen.getByPlaceholderText('62701'), '62701')
    await userEvent.type(screen.getByPlaceholderText('e.g. 1200'), '1200')
    await userEvent.click(screen.getByText('Get Estimate →'))
    await waitFor(() => screen.getByText('Your Estimate'))
  }

  it('shows price and Book Now button', async () => {
    await advanceToResult()
    expect(screen.getByText('$150.00')).toBeInTheDocument()
    expect(screen.getByText('Book Now')).toBeInTheDocument()
  })

  it('advances to booking screen on Book Now', async () => {
    await advanceToResult()
    await userEvent.click(screen.getByText('Book Now'))
    await waitFor(() => expect(screen.getByText('Book Your Appointment')).toBeInTheDocument())
  })
})

// ── Screen 3: Booking ──────────────────────────────────────────────────────────

describe('EstimateFlow — booking screen (screen 3)', () => {
  async function advanceToBooking() {
    global.fetch = mockFetch({
      '/api/v1/services/estimate': {
        estimated_price_display: '$150.00',
        estimated_price_cents: 15000,
        address: '123 Maple Ave, Springfield, IL 62701',
      },
      '/api/v1/intake/openings': ['2099-06-01T09:00:00', '2099-06-01T11:00:00', '2099-06-02T09:00:00'],
    }) as typeof fetch

    renderFlow()
    await userEvent.selectOptions(screen.getByRole('combobox'), 'pwash')
    await userEvent.type(screen.getByPlaceholderText('123'), '123')
    await userEvent.type(screen.getByPlaceholderText('Maple Ave'), 'Maple Ave')
    await userEvent.type(screen.getByPlaceholderText('Springfield'), 'Springfield')
    await userEvent.type(screen.getByPlaceholderText('IL'), 'IL')
    await userEvent.type(screen.getByPlaceholderText('62701'), '62701')
    await userEvent.type(screen.getByPlaceholderText('e.g. 1200'), '1200')
    await userEvent.click(screen.getByText('Get Estimate →'))
    await waitFor(() => screen.getByText('Your Estimate'))
    await userEvent.click(screen.getByText('Book Now'))
    await waitFor(() => screen.getByText('Book Your Appointment'))
  }

  it('renders contact fields and time slots', async () => {
    await advanceToBooking()
    expect(screen.getByPlaceholderText('Jane Smith')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('123-456-7890')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('jane@example.com')).toBeInTheDocument()
    expect(screen.getAllByText(/Jun 1/i).length).toBeGreaterThan(0)
  })

  it('Book Now button is disabled until slot and all fields are filled', async () => {
    await advanceToBooking()
    const bookBtn = screen.getAllByText('Book Now').find(
      (el) => el.tagName === 'BUTTON'
    ) as HTMLButtonElement
    expect(bookBtn).toBeDisabled()
  })

  it('calls /api/v1/intake/book and shows success screen', async () => {
    await advanceToBooking()

    // Fill contact info
    await userEvent.type(screen.getByPlaceholderText('Jane Smith'), 'Jane Smith')
    await userEvent.type(screen.getByPlaceholderText('123-456-7890'), '404-234-5678')
    await userEvent.type(screen.getByPlaceholderText('jane@example.com'), 'jane@example.com')

    // Pick first slot
    const slots = screen.getAllByRole('button').filter((b) => b.textContent?.includes('Jun'))
    await userEvent.click(slots[0])

    // Swap fetch to handle the booking POST
    global.fetch = vi.fn(() =>
      Promise.resolve({ ok: true, status: 201, json: () => Promise.resolve({ booking_id: 'abc-123', message: 'Booking confirmed!' }) })
    ) as typeof fetch

    const bookBtn = screen.getAllByText('Book Now').find(
      (el) => el.tagName === 'BUTTON'
    ) as HTMLButtonElement
    await userEvent.click(bookBtn)

    await waitFor(() => expect(screen.getByText('Booking Confirmed')).toBeInTheDocument())
  })

  it('shows error message when booking API returns a conflict', async () => {
    await advanceToBooking()

    await userEvent.type(screen.getByPlaceholderText('Jane Smith'), 'Jane Smith')
    await userEvent.type(screen.getByPlaceholderText('123-456-7890'), '404-234-5678')
    await userEvent.type(screen.getByPlaceholderText('jane@example.com'), 'jane@example.com')

    const slots = screen.getAllByRole('button').filter((b) => b.textContent?.includes('Jun'))
    await userEvent.click(slots[0])

    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: false, status: 409,
        json: () => Promise.resolve({ detail: 'That slot was just taken. Please pick another time.' }),
      })
    ) as typeof fetch

    const bookBtn = screen.getAllByText('Book Now').find(
      (el) => el.tagName === 'BUTTON'
    ) as HTMLButtonElement
    await userEvent.click(bookBtn)

    await waitFor(() =>
      expect(screen.getByText('That slot was just taken. Please pick another time.')).toBeInTheDocument()
    )
  })
})

// ── App navbar ─────────────────────────────────────────────────────────────────

describe('App navbar branding', () => {
  it('shows 360 Home Services in the nav', async () => {
    const { render: _render } = await import('@testing-library/react')
    const { default: App } = await import('../App')
    _render(<MemoryRouter><App /></MemoryRouter>)
    expect(screen.getByText('360 Home Services')).toBeInTheDocument()
  })
})
