import React from 'react';
import { Link } from 'react-router-dom';
import { ShoppingCart, MessageSquare } from 'lucide-react';
import { useAppContext } from '../context/AppContext';

const Navbar: React.FC = () => {
  const { cart, toggleChat } = useAppContext();
  const cartItemCount = cart.reduce((total, item) => total + item.quantity, 0);

  return (
    <header className="w-full bg-[#F4F1EB] pt-6 px-6 md:px-12 lg:px-24 z-40">
      <div className="editorial-border flex items-center justify-between">
        <div className="w-1/3">
          <Link to="/products" className="text-sm font-medium uppercase tracking-widest hover:text-[#C86B5E] transition-colors relative group">
            Shop Collection
            <span className="absolute -bottom-1 left-0 w-0 h-[1px] bg-[#C86B5E] transition-all duration-300 group-hover:w-full"></span>
          </Link>
        </div>

        <div className="w-1/3 flex justify-center">
          <Link to="/" className="font-serif text-3xl md:text-4xl text-[#1C1B1A] tracking-tight">
            Cartostrophe.
          </Link>
        </div>

        <div className="w-1/3 flex items-center justify-end gap-6">
          <button 
            onClick={toggleChat} 
            className="flex items-center gap-2 text-sm font-medium uppercase tracking-widest hover:text-[#7C8973] transition-colors relative group"
            aria-label="Toggle AI Chat"
          >
            <MessageSquare size={16} className="hidden sm:block" />
            <span>AI Assistant</span>
            <span className="absolute -bottom-1 left-0 w-0 h-[1px] bg-[#7C8973] transition-all duration-300 group-hover:w-full"></span>
          </button>
          
          <Link to="/cart" className="relative flex items-center hover:text-[#D9A05B] transition-colors group">
            <span className="sr-only">Cart</span>
            <ShoppingCart size={20} />
            <span className="absolute -bottom-2 left-0 w-0 h-[1px] bg-[#D9A05B] transition-all duration-300 group-hover:w-full"></span>
            
            {cartItemCount > 0 && (
              <span className="absolute -top-2 -right-3 w-5 h-5 flex items-center justify-center text-[10px] font-bold text-[#F4F1EB] bg-[#1C1B1A] rounded-full">
                {cartItemCount}
              </span>
            )}
          </Link>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
