import { Routes, Route, NavLink } from 'react-router-dom'
import ClientInformation from './components/ClientInformation'
import EstimateFlow from './components/EstimateFlow'

function NavBar() {
  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `px-4 py-2 rounded-md text-sm font-medium transition-colors ${
      isActive
        ? 'bg-brand text-white'
        : 'text-white/80 hover:bg-brand hover:text-white'
    }`

  return (
    <nav className="bg-nav shadow-md">
      <div className="max-w-5xl mx-auto px-4 py-3 flex items-center gap-6">
        <NavLink to="/" className="text-white font-bold text-lg tracking-tight">
          360 Home Services
        </NavLink>
        <div className="flex gap-2">
          <NavLink to="/estimate" className={linkClass}>
            Get Estimate
          </NavLink>
        </div>
      </div>
    </nav>
  )
}

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <NavBar />
      <main className="max-w-5xl mx-auto px-4 py-8">
        <Routes>
          <Route path="/" element={<EstimateFlow />} />
          <Route path="/estimate" element={<EstimateFlow />} />
          <Route path="/clients/new" element={<ClientInformation />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
