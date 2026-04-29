import React from 'react';
import { Link } from 'react-router-dom';
import { Minus, Plus, ArrowRight } from 'lucide-react';
import { useAppContext } from '../context/AppContext';

const Cart: React.FC = () => {
  const { cart, updateQuantity, clearCart } = useAppContext();

  const total = cart.reduce((sum, item) => sum + item.product.price * item.quantity, 0);

  if (cart.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center border-y-2 border-[#1C1B1A] py-24 animate-slide-up">
        <p className="text-xs font-bold uppercase tracking-[0.2em] text-[#C86B5E] mb-6">Status</p>
        <h2 className="font-serif text-5xl md:text-6xl text-[#1C1B1A] mb-8 italic">Cart is Empty.</h2>
        <Link to="/products" className="inline-flex items-center gap-4 border-b-2 border-[#1C1B1A] pb-2 text-sm font-bold uppercase tracking-widest hover:text-[#C86B5E] hover:border-[#C86B5E] transition-colors group">
          Curate your collection <ArrowRight size={16} className="transform group-hover:translate-x-2 transition-transform" />
        </Link>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-16 pb-20 animate-slide-up delay-100">
      <header className="border-b-2 border-[#1C1B1A] pb-8 flex items-end justify-between">
        <div>
          <h1 className="font-serif text-5xl md:text-7xl text-[#1C1B1A] tracking-tighter">Cart.</h1>
        </div>
        <button 
          onClick={clearCart} 
          className="text-xs font-bold uppercase tracking-widest text-[#1C1B1A]/60 hover:text-[#C86B5E] transition-colors pb-2"
        >
          [ Clear Cart ]
        </button>
      </header>

      <div className="flex flex-col lg:flex-row gap-16 items-start">
        <div className="w-full lg:w-2/3">
          {/* Table Header */}
          <div className="grid grid-cols-12 gap-4 pb-4 border-b border-[#1C1B1A]/20 text-[10px] font-bold uppercase tracking-widest opacity-60">
            <div className="col-span-6 md:col-span-7">Item</div>
            <div className="col-span-3 md:col-span-2 text-center">Qty</div>
            <div className="col-span-3 text-right">Price</div>
          </div>

          {/* Cart Items */}
          <div className="flex flex-col">
            {cart.map((item) => (
              <div key={item.product.id} className="grid grid-cols-12 gap-4 py-8 border-b border-[#1C1B1A]/20 items-center group">
                <div className="col-span-6 md:col-span-7 flex flex-col">
                  <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-[#D9A05B] mb-2">
                    {item.product.category}
                  </span>
                  <h3 className="font-serif text-2xl md:text-3xl text-[#1C1B1A] leading-none mb-2 group-hover:text-[#C86B5E] transition-colors">
                    {item.product.name_en}
                  </h3>
                  <p className="text-xs opacity-60" dir="rtl">{item.product.name_ar}</p>
                </div>
                
                <div className="col-span-3 md:col-span-2 flex justify-center">
                  <div className="flex items-center gap-3 border border-[#1C1B1A] p-1">
                    <button 
                      onClick={() => updateQuantity(item.product.id, item.quantity - 1)}
                      className="w-6 h-6 flex items-center justify-center text-[#1C1B1A] hover:bg-[#1C1B1A] hover:text-[#F4F1EB] transition-colors"
                      aria-label="Decrease quantity"
                    >
                      <Minus size={12} />
                    </button>
                    <span className="text-xs font-bold w-4 text-center">
                      {item.quantity}
                    </span>
                    <button 
                      onClick={() => updateQuantity(item.product.id, item.quantity + 1)}
                      className="w-6 h-6 flex items-center justify-center text-[#1C1B1A] hover:bg-[#1C1B1A] hover:text-[#F4F1EB] transition-colors"
                      aria-label="Increase quantity"
                    >
                      <Plus size={12} />
                    </button>
                  </div>
                </div>

                <div className="col-span-3 text-right flex flex-col items-end">
                  <span className="text-[10px] font-bold uppercase tracking-widest opacity-60 mb-1">{item.product.currency}</span>
                  <span className="font-serif text-2xl md:text-3xl">{(item.product.price * item.quantity).toFixed(2)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="w-full lg:w-1/3 bg-[#1C1B1A] text-[#F4F1EB] p-8 md:p-12 sticky top-24">
          <h2 className="font-serif text-3xl mb-12 italic border-b border-[#F4F1EB]/20 pb-6">Summary</h2>
          
          <div className="space-y-6 text-sm font-medium tracking-wide">
            <div className="flex justify-between">
              <span className="opacity-70">Subtotal [{cart.reduce((acc, item) => acc + item.quantity, 0)}]</span>
              <span>AED {total.toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span className="opacity-70">Logistics</span>
              <span className="text-[#D9A05B]">Complimentary</span>
            </div>
          </div>
          
          <div className="mt-12 pt-8 border-t border-[#F4F1EB]/20 flex justify-between items-end">
            <span className="text-xs font-bold uppercase tracking-widest opacity-70">Total</span>
            <div className="text-right">
              <span className="font-serif text-5xl">
                {total.toFixed(2)}
              </span>
            </div>
          </div>
          
          <button className="w-full mt-12 flex items-center justify-between bg-[#F4F1EB] text-[#1C1B1A] px-6 py-5 text-sm font-bold uppercase tracking-widest hover:bg-[#C86B5E] hover:text-[#F4F1EB] transition-colors duration-500 group">
            <span>Procure Items</span>
            <ArrowRight size={18} className="transform group-hover:translate-x-2 transition-transform duration-500" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default Cart;
