import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Sparkles, ShieldCheck, Truck } from 'lucide-react';
import { useAppContext } from '../context/AppContext';

const Landing: React.FC = () => {
  const { toggleChat } = useAppContext();

  return (
    <div className="flex flex-col gap-24 pb-20 animate-slide-up">
      {/* Hero Section */}
      <section className="relative pt-12 lg:pt-24 flex flex-col lg:flex-row items-end gap-16">
        <div className="w-full lg:w-2/3 space-y-8 z-10">
          <h1 className="font-serif text-6xl md:text-8xl lg:text-[7rem] leading-[0.9] text-[#1C1B1A] tracking-tighter">
            Curated <br />
            <span className="italic text-[#7C8973]">Essentials</span> <br />
            For Modern <br />
            Parenting.
          </h1>
          <div className="pt-8 w-full max-w-md">
            <p className="text-lg text-[#1C1B1A]/80 leading-relaxed font-medium">
              We reject the generic. Discover a meticulously selected collection of the finest products for your little ones, guided by our intelligent assistant.
            </p>
          </div>
          <div className="flex flex-col sm:flex-row gap-6 pt-4">
            <Link to="/products" className="inline-flex items-center justify-between bg-[#1C1B1A] text-[#F4F1EB] px-8 py-4 text-sm font-bold uppercase tracking-widest hover:bg-[#C86B5E] transition-colors duration-500 w-fit gap-8 group">
              <span>View Catalog</span> 
              <ArrowRight size={18} className="transform group-hover:translate-x-2 transition-transform duration-500" />
            </Link>
            <button onClick={toggleChat} className="inline-flex items-center justify-center gap-3 border-b-2 border-[#1C1B1A] text-[#1C1B1A] px-2 py-4 text-sm font-bold uppercase tracking-widest hover:text-[#7C8973] hover:border-[#7C8973] transition-colors duration-500 w-fit">
              <Sparkles size={16} /> Consult AI Assistant
            </button>
          </div>
        </div>
        
        <div className="w-full lg:w-1/3 h-[500px] bg-[#1C1B1A] p-8 flex flex-col justify-between animate-image-reveal relative overflow-hidden">
           <div className="absolute top-0 right-0 w-64 h-64 bg-[#C86B5E] rounded-full blur-[100px] opacity-40"></div>
           <div className="absolute bottom-0 left-0 w-64 h-64 bg-[#7C8973] rounded-full blur-[100px] opacity-40"></div>
           
           <div className="relative z-10 text-[#F4F1EB]">
             <span className="font-serif text-5xl">01</span>
             <div className="w-full h-[1px] bg-[#F4F1EB]/30 my-4"></div>
             <p className="text-sm font-medium uppercase tracking-widest">Featured Collection</p>
           </div>
           
           <div className="relative z-10 space-y-4 text-[#F4F1EB]">
             <h3 className="font-serif text-3xl italic">The Art of <br/> Simplification</h3>
             <p className="text-sm text-[#F4F1EB]/70 max-w-[200px] leading-relaxed">
               Quality over quantity. Objects designed to last and delight.
             </p>
           </div>
        </div>
      </section>

      <div className="editorial-divider"></div>

      {/* Features Section */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-0 border-y border-[#1C1B1A]/20">
        <div className="p-8 md:p-12 border-b md:border-b-0 md:border-r border-[#1C1B1A]/20 hover:bg-[#F4F1EB] transition-colors group">
          <div className="text-[#D9A05B] mb-8 transform group-hover:scale-110 transition-transform duration-500 origin-left">
            <Sparkles size={32} strokeWidth={1.5} />
          </div>
          <h3 className="font-serif text-2xl text-[#1C1B1A] mb-4">Intelligent Curation</h3>
          <p className="text-[#1C1B1A]/70 leading-relaxed text-sm">Speak naturally. Our AI assistant understands context and nuance, building your perfect cart in seconds.</p>
        </div>
        <div className="p-8 md:p-12 border-b md:border-b-0 md:border-r border-[#1C1B1A]/20 hover:bg-[#F4F1EB] transition-colors group">
          <div className="text-[#7C8973] mb-8 transform group-hover:scale-110 transition-transform duration-500 origin-left">
            <ShieldCheck size={32} strokeWidth={1.5} />
          </div>
          <h3 className="font-serif text-2xl text-[#1C1B1A] mb-4">Uncompromising Quality</h3>
          <p className="text-[#1C1B1A]/70 leading-relaxed text-sm">We reject the ordinary. Every item is rigorously vetted for safety, aesthetics, and lasting value.</p>
        </div>
        <div className="p-8 md:p-12 hover:bg-[#F4F1EB] transition-colors group">
          <div className="text-[#C86B5E] mb-8 transform group-hover:scale-110 transition-transform duration-500 origin-left">
            <Truck size={32} strokeWidth={1.5} />
          </div>
          <h3 className="font-serif text-2xl text-[#1C1B1A] mb-4">White-Glove Delivery</h3>
          <p className="text-[#1C1B1A]/70 leading-relaxed text-sm">Your essentials arrive beautifully packaged and promptly delivered, directly to your door.</p>
        </div>
      </section>
    </div>
  );
};

export default Landing;
