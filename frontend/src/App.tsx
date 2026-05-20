import { Routes, Route, NavLink } from 'react-router-dom'
import ClientInformation from './components/ClientInformation'

function NavBar() {
  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `px-4 py-2 rounded-md text-sm font-medium transition-colors ${
      isActive
        ? 'bg-green-700 text-white'
        : 'text-green-100 hover:bg-green-700 hover:text-white'
    }`

  return (
    <nav className="bg-green-800 shadow-md">
      <div className="max-w-5xl mx-auto px-4 py-3 flex items-center gap-6">
        <span className="text-white font-bold text-lg tracking-tight">
          LandscapePro
        </span>
        <div className="flex gap-2">
          <NavLink to="/clients/new" className={linkClass}>
            New Client
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
          <Route path="/" element={<ClientInformation />} />
          <Route path="/clients/new" element={<ClientInformation />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
