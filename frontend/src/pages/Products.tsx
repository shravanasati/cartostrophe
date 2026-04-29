import React, { useState, useMemo } from 'react';
import { useAppContext } from '../context/AppContext';
import ProductCard from '../components/ProductCard';

const Products: React.FC = () => {
  const { products } = useAppContext();

  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [filterTarget, setFilterTarget] = useState<string>('all');
  const [filterMaxPrice, setFilterMaxPrice] = useState<number | ''>('');

  // Extract unique categories and targets dynamically
  const categories = useMemo(() => Array.from(new Set(products.map(p => p.category))), [products]);
  const targets = useMemo(() => Array.from(new Set(products.map(p => p.target_customer).filter(Boolean))), [products]);

  const filteredProducts = useMemo(() => {
    return products.filter(p => {
      if (filterCategory !== 'all' && p.category !== filterCategory) return false;
      if (filterTarget !== 'all' && p.target_customer !== filterTarget) return false;
      if (filterMaxPrice !== '' && p.price > filterMaxPrice) return false;
      return true;
    });
  }, [products, filterCategory, filterTarget, filterMaxPrice]);

  return (
    <div className="flex flex-col gap-12 pb-20 animate-slide-up delay-100">
      <header className="border-b-2 border-[#1C1B1A] pb-8 flex flex-col md:flex-row items-end justify-between gap-8">
        <div>
          <h1 className="font-serif text-5xl md:text-7xl text-[#1C1B1A] tracking-tighter">The Collection.</h1>
        </div>
        <div className="text-right flex flex-col items-end">
          <p className="text-sm font-bold uppercase tracking-widest text-[#1C1B1A]">
            [{filteredProducts.length.toString().padStart(3, '0')}] Objects
          </p>
          <p className="text-xs text-[#1C1B1A]/70 mt-2 max-w-[200px]">
            Meticulously curated for the modern nursery.
          </p>
        </div>
      </header>

      {/* Editorial Filter Bar */}
      {products.length > 0 && (
        <div className="flex flex-col md:flex-row gap-8 items-start md:items-center border-b border-[#1C1B1A]/20 pb-8">
          <span className="text-[10px] font-bold uppercase tracking-[0.2em] opacity-50 shrink-0">
            Index / Filter
          </span>
          
          <div className="flex flex-wrap gap-6 items-center">
            <select 
              className="bg-transparent border-b border-[#1C1B1A] text-xs font-bold uppercase tracking-widest focus:outline-none py-1 cursor-pointer hover:text-[#C86B5E] transition-colors appearance-none pr-4"
              value={filterCategory}
              onChange={e => setFilterCategory(e.target.value)}
            >
              <option value="all">Category: All</option>
              {categories.map(c => <option key={c} value={c}>Category: {c}</option>)}
            </select>
            
            <select 
              className="bg-transparent border-b border-[#1C1B1A] text-xs font-bold uppercase tracking-widest focus:outline-none py-1 cursor-pointer hover:text-[#C86B5E] transition-colors appearance-none pr-4"
              value={filterTarget}
              onChange={e => setFilterTarget(e.target.value)}
            >
              <option value="all">Target: All</option>
              {targets.map(t => <option key={t as string} value={t as string}>Target: {t}</option>)}
            </select>
            
            <div className="flex items-center gap-2 border-b border-[#1C1B1A] py-1 hover:text-[#C86B5E] transition-colors group">
              <span className="text-xs font-bold uppercase tracking-widest">Max Price:</span>
              <input 
                type="number" 
                placeholder="ANY"
                className="bg-transparent w-16 text-xs font-bold uppercase tracking-widest focus:outline-none text-right placeholder-[#1C1B1A]/30 group-hover:text-[#C86B5E]"
                value={filterMaxPrice}
                onChange={e => setFilterMaxPrice(e.target.value ? Number(e.target.value) : '')}
                min="0"
              />
            </div>
            
            {(filterCategory !== 'all' || filterTarget !== 'all' || filterMaxPrice !== '') && (
              <button 
                onClick={() => {
                  setFilterCategory('all');
                  setFilterTarget('all');
                  setFilterMaxPrice('');
                }}
                className="text-[10px] font-bold uppercase tracking-widest text-[#C86B5E] hover:text-[#1C1B1A] transition-colors ml-4"
              >
                [ Clear ]
              </button>
            )}
          </div>
        </div>
      )}
      
      {products.length === 0 ? (
        <div className="h-[40vh] flex flex-col items-center justify-center border border-[#1C1B1A]/20">
          <div className="font-serif text-2xl animate-pulse italic">Curating...</div>
        </div>
      ) : filteredProducts.length === 0 ? (
        <div className="h-[40vh] flex flex-col items-center justify-center border border-[#1C1B1A]/20">
          <div className="font-serif text-2xl italic text-[#1C1B1A]/60">No objects match this criteria.</div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-0 border-t border-l border-[#1C1B1A]">
          {filteredProducts.map((product) => (
            <div key={product.id} className="border-r border-b border-[#1C1B1A]">
              <ProductCard product={product} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Products;
