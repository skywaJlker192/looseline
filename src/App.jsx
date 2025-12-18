import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import BetsPage from './bets/pages/BetsPage.jsx'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<BetsPage />} />
      </Routes>
    </Router>
  )
}

export default App