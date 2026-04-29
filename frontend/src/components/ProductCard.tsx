import React from 'react';
import { useAppContext } from '../context/AppContext';
import { Plus } from 'lucide-react';
import type { Product } from '../services/api';

interface ProductCardProps {
  product: Product;
}

const ProductCard: React.FC<ProductCardProps> = ({ product }) => {
  const { addToCart } = useAppContext();

  return (
    <article className="group flex flex-col h-full border border-[#1C1B1A] bg-[#F4F1EB] hover:bg-[#1C1B1A] hover:text-[#F4F1EB] transition-colors duration-500 relative overflow-hidden">
      
      {/* Decorative top border */}
      <div className="h-1 w-full bg-[#1C1B1A] group-hover:bg-[#C86B5E] transition-colors duration-500"></div>

      <div className="p-6 flex flex-col flex-grow z-10 relative">
        <div className="flex justify-between items-start mb-8">
          <span className="text-[10px] font-bold uppercase tracking-[0.2em] group-hover:text-[#F4F1EB]/80">
            {product.category}
          </span>
          <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-[#D9A05B]">
            No. {product.id.toString().padStart(3, '0')}
          </span>
        </div>
        
        <h3 className="font-serif text-3xl leading-tight mb-2 pr-4">
          {product.name_en}
        </h3>
        <p className="text-sm font-medium mb-6 opacity-70" dir="rtl">{product.name_ar}</p>
        
        <div className="w-8 h-[1px] bg-[#1C1B1A] group-hover:bg-[#F4F1EB] mb-6 transition-colors duration-500"></div>
        
        <p className="text-xs leading-relaxed opacity-80 mb-8 flex-grow">
          {product.description_en}
        </p>
        
        <div className="flex flex-wrap gap-2 mb-10">
          {product.attributes.slice(0, 3).map((attr, index) => (
            <span key={index} className="text-[10px] uppercase tracking-wider border border-[#1C1B1A]/20 group-hover:border-[#F4F1EB]/20 px-2 py-1">
              {attr.replace(/-/g, ' ')}
            </span>
          ))}
        </div>
        
        <div className="flex items-end justify-between mt-auto">
          <div className="flex flex-col">
            <span className="text-[10px] font-bold uppercase tracking-widest opacity-60 mb-1">{product.currency}</span>
            <span className="font-serif text-3xl leading-none">{product.price.toFixed(2)}</span>
          </div>
          <button 
            className="w-12 h-12 flex items-center justify-center border border-[#1C1B1A] group-hover:border-[#F4F1EB] group-hover:bg-[#F4F1EB] group-hover:text-[#1C1B1A] transition-all duration-300"
            onClick={() => addToCart(product.id, 1)}
            aria-label="Add to cart"
          >
            <Plus size={20} strokeWidth={1.5} className="transform group-hover:rotate-90 transition-transform duration-500" />
          </button>
        </div>
      </div>
    </article>
  );
};

export default ProductCard;
