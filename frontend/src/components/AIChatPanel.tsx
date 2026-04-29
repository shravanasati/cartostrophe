import React, { useState, useRef, useEffect } from 'react';
import { Mic, Send, X, ShoppingCart, Volume2, Square } from 'lucide-react';
import { useAppContext } from '../context/AppContext';
import { searchProducts } from '../services/api';

interface Message {
  id: string;
  sender: 'user' | 'ai';
  text: string;
  isArabic?: boolean;
  productIds?: number[];
}

const AIChatPanel: React.FC = () => {
  const { isChatOpen, toggleChat, addToCart } = useAppContext();
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    { id: '1', sender: 'ai', text: 'Welcome. I am the Cartostrophe Assistant. How may I assist in curating your collection today?' }
  ]);
  const [isRecording, setIsRecording] = useState(false);
  const [speechLang, setSpeechLang] = useState<'en-US' | 'ar-SA'>('en-US');
  const [isLoading, setIsLoading] = useState(false);
  const [speakingMessageId, setSpeakingMessageId] = useState<string | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;

      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInput(transcript);
        setIsRecording(false);
      };

      recognitionRef.current.onerror = (event: any) => {
        console.error("Speech recognition error", event.error);
        setIsRecording(false);
      };
      
      recognitionRef.current.onend = () => {
        setIsRecording(false);
      };
    }
  }, [SpeechRecognition]);

  useEffect(() => {
    if (recognitionRef.current) {
      recognitionRef.current.lang = speechLang;
    }
  }, [speechLang]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const isArabicText = (text: string) => {
    const arabicRegex = /[\u0600-\u06FF]/;
    return arabicRegex.test(text);
  };

  const speakMessage = (id: string, text: string, isArabic?: boolean) => {
    if (!('speechSynthesis' in window)) {
      alert("Text-to-speech is not supported in this browser.");
      return;
    }
    window.speechSynthesis.cancel(); // Stop any ongoing speech
    
    if (speakingMessageId === id) {
      setSpeakingMessageId(null);
      return;
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = isArabic ? 'ar-SA' : 'en-US';
    
    utterance.onend = () => setSpeakingMessageId(null);
    utterance.onerror = () => setSpeakingMessageId(null);

    setSpeakingMessageId(id);
    window.speechSynthesis.speak(utterance);
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    const userText = input.trim();
    const isArabic = isArabicText(userText);
    
    const newUserMsg: Message = { id: Date.now().toString(), sender: 'user', text: userText, isArabic };
    setMessages(prev => [...prev, newUserMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const result = await searchProducts(userText);
      if (result && result.ids.length > 0) {
        result.ids.forEach(id => addToCart(id, 1));
        
        const responseText = isArabic ? result.reasoning_ar : result.reasoning_en;
        
        const aiMsg: Message = {
          id: (Date.now() + 1).toString(),
          sender: 'ai',
          text: responseText || 'Items procured.',
          isArabic,
          productIds: result.ids
        };
        setMessages(prev => [...prev, aiMsg]);
      } else {
        const aiMsg: Message = {
          id: (Date.now() + 1).toString(),
          sender: 'ai',
          text: isArabic ? 'عذراً، لم أتمكن من العثور على أي منتجات مطابقة.' : 'Apologies. No matching items found in the current collection.',
          isArabic
        };
        setMessages(prev => [...prev, aiMsg]);
      }
    } catch (error) {
      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        text: 'An error occurred during retrieval.',
      };
      setMessages(prev => [...prev, aiMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleRecording = () => {
    if (isRecording) {
      recognitionRef.current?.stop();
      setIsRecording(false);
    } else {
      if (recognitionRef.current) {
        recognitionRef.current.start();
        setIsRecording(true);
      } else {
        alert("Speech recognition is not supported in this browser.");
      }
    }
  };

  const toggleLang = () => {
    setSpeechLang(prev => prev === 'en-US' ? 'ar-SA' : 'en-US');
  };

  if (!isChatOpen) return null;

  return (
    <div className="fixed bottom-0 right-0 md:bottom-8 md:right-8 w-full md:w-[450px] h-[600px] max-h-screen bg-[#F4F1EB] border-2 border-[#1C1B1A] flex flex-col z-50 animate-slide-up shadow-[16px_16px_0px_0px_rgba(28,27,26,1)]">
      {/* Header */}
      <div className="bg-[#1C1B1A] text-[#F4F1EB] p-6 flex items-center justify-between border-b-2 border-[#1C1B1A]">
        <div>
          <h3 className="font-serif text-2xl tracking-wide italic">AI Assistant</h3>
        </div>
        <button onClick={toggleChat} className="text-[#F4F1EB]/50 hover:text-[#C86B5E] transition-colors" aria-label="Close Assistant">
          <X size={24} strokeWidth={1.5} />
        </button>
      </div>
      
      {/* Message Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-8 bg-[#F4F1EB] noise-overlay-container" style={{ position: 'relative' }}>
        {messages.map(msg => (
          <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div 
              className={`max-w-[85%] ${
                msg.sender === 'user' 
                  ? 'border-b border-l border-[#1C1B1A] pl-4 pb-4' 
                  : 'border-t border-r border-[#1C1B1A] pr-4 pt-4'
              }`}
              dir={msg.isArabic ? 'rtl' : 'ltr'}
            >
              <p className="text-[10px] font-bold uppercase tracking-[0.2em] mb-2 opacity-50">
                {msg.sender === 'user' ? 'Client' : 'Assistant'}
              </p>
              <div className="flex items-start justify-between gap-4">
                <p className={`text-sm leading-relaxed ${msg.sender === 'ai' ? 'font-serif text-lg italic' : ''}`}>
                  {msg.text}
                </p>
                {msg.sender === 'ai' && (
                  <button 
                    onClick={() => speakMessage(msg.id, msg.text, msg.isArabic)}
                    className="text-[#1C1B1A]/40 hover:text-[#C86B5E] transition-colors mt-1"
                    aria-label={speakingMessageId === msg.id ? "Stop speaking" : "Speak message"}
                    title={speakingMessageId === msg.id ? "Stop speaking" : "Speak message"}
                  >
                    {speakingMessageId === msg.id ? (
                      <Square size={16} strokeWidth={2} />
                    ) : (
                      <Volume2 size={16} strokeWidth={2} />
                    )}
                  </button>
                )}
              </div>
              {msg.productIds && msg.productIds.length > 0 && (
                <div className="mt-4 pt-4 border-t border-[#1C1B1A]/20 flex items-center gap-2">
                  <div className="w-6 h-6 bg-[#1C1B1A] text-[#F4F1EB] flex items-center justify-center">
                    <ShoppingCart size={12} />
                  </div>
                  <span className="text-[10px] font-bold uppercase tracking-widest text-[#7C8973]">
                    {msg.productIds.length} Object{msg.productIds.length > 1 ? 's' : ''} added
                  </span>
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="border-t border-r border-[#1C1B1A] pr-4 pt-4">
               <p className="text-[10px] font-bold uppercase tracking-[0.2em] mb-2 opacity-50">Assistant</p>
               <div className="flex items-center gap-1.5 py-2">
                 <span className="w-1.5 h-1.5 bg-[#1C1B1A] typing-dot"></span>
                 <span className="w-1.5 h-1.5 bg-[#1C1B1A] typing-dot"></span>
                 <span className="w-1.5 h-1.5 bg-[#1C1B1A] typing-dot"></span>
               </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-[#F4F1EB] border-t-2 border-[#1C1B1A]">
        <div className="flex items-stretch h-16">
          <button 
            onClick={toggleLang} 
            className="px-6 border-r-2 border-[#1C1B1A] text-[10px] font-bold uppercase tracking-widest hover:bg-[#1C1B1A] hover:text-[#F4F1EB] transition-colors"
            title={`Language: ${speechLang === 'en-US' ? 'English' : 'Arabic'}`}
          >
            {speechLang === 'en-US' ? 'EN' : 'AR'}
          </button>
          
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="State your request..."
            className="flex-1 bg-transparent border-none focus:outline-none text-sm px-6 italic placeholder-[#1C1B1A]/30"
            dir="auto"
          />
          
          <button 
            onClick={toggleRecording} 
            className={`px-6 border-l-2 border-[#1C1B1A] transition-colors ${
              isRecording ? 'bg-[#C86B5E] text-[#F4F1EB]' : 'hover:bg-[#1C1B1A] hover:text-[#F4F1EB] text-[#1C1B1A]'
            }`}
            aria-label={isRecording ? 'Stop Recording' : 'Dictate'}
          >
            <Mic size={18} strokeWidth={1.5} />
          </button>
          
          <button 
            onClick={handleSend} 
            className="w-16 bg-[#1C1B1A] text-[#F4F1EB] flex items-center justify-center hover:bg-[#D9A05B] hover:text-[#1C1B1A] transition-colors disabled:opacity-50 disabled:cursor-not-allowed" 
            disabled={!input.trim() || isLoading}
          >
            <Send size={18} strokeWidth={1.5} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default AIChatPanel;
