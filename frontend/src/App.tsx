import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import AIChatPanel from './components/AIChatPanel';
import Landing from './pages/Landing';
import Products from './pages/Products';
import Cart from './pages/Cart';
import { AppProvider } from './context/AppContext';

function App() {
  return (
    <AppProvider>
      {/* Global Noise Texture Overlay */}
      <div className="noise-overlay"></div>
      
      <div className="min-h-screen flex flex-col relative pb-20 overflow-x-hidden selection:bg-[#C86B5E] selection:text-[#F4F1EB]">
        <Navbar />
        <main className="flex-grow w-full px-6 py-12 md:px-12 lg:px-24">
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/products" element={<Products />} />
            <Route path="/cart" element={<Cart />} />
          </Routes>
        </main>
        <AIChatPanel />
      </div>
    </AppProvider>
  );
}

export default App;
