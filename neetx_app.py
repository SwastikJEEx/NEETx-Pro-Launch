<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NEETx - AI Learning Assistant</title>
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- React & ReactDOM -->
    <script crossorigin src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    
    <!-- Babel -->
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    
    <!-- Lucide Icons -->
    <script src="https://unpkg.com/lucide@latest"></script>

    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">

    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f0fdf4; /* Light Green bg */
        }
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-track {
            background: transparent;
        }
        ::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #94a3b8;
        }

        /* 3D Flip Animation */
        .perspective-1000 {
            perspective: 1000px;
        }
        .transform-style-3d {
            transform-style: preserve-3d;
        }
        .backface-hidden {
            backface-visibility: hidden;
        }
        .rotate-y-180 {
            transform: rotateY(180deg);
        }

        /* Glassmorphism */
        .glass-panel {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        /* Loader */
        .loader {
            border: 3px solid #f3f3f3;
            border-radius: 50%;
            border-top: 3px solid #059669;
            width: 24px;
            height: 24px;
            -webkit-animation: spin 1s linear infinite; /* Safari */
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div id="root"></div>

    <script type="text/babel">
        // --- Constants & Data ---
        const NEET_SYLLABUS = {
            "Physics": [
                "Physical World and Measurement", "Kinematics", "Laws of Motion", "Work, Energy and Power",
                "Motion of System of Particles", "Gravitation", "Properties of Bulk Matter", "Thermodynamics",
                "Oscillations and Waves", "Electrostatics", "Current Electricity", "Magnetic Effects of Current",
                "Magnetism", "Electromagnetic Induction", "Alternating Currents", "Electromagnetic Waves",
                "Optics", "Dual Nature of Matter", "Atoms and Nuclei", "Electronic Devices"
            ],
            "Chemistry": [
                "Some Basic Concepts of Chemistry", "Structure of Atom", "Classification of Elements",
                "Chemical Bonding", "States of Matter", "Thermodynamics", "Equilibrium", "Redox Reactions",
                "Hydrogen", "s-Block Elements", "p-Block Elements", "Organic Chemistry - Basic Principles",
                "Hydrocarbons", "Environmental Chemistry", "Solid State", "Solutions", "Electrochemistry",
                "Chemical Kinetics", "Surface Chemistry", "Coordination Compounds", "Haloalkanes and Haloarenes",
                "Alcohols, Phenols and Ethers", "Aldehydes, Ketones and Carboxylic Acids", "Amines", "Biomolecules",
                "Polymers", "Chemistry in Everyday Life"
            ],
            "Biology": [
                "Diversity in Living World", "Structural Organisation in Animals and Plants", "Cell Structure and Function",
                "Plant Physiology", "Human Physiology", "Reproduction", "Genetics and Evolution",
                "Biology and Human Welfare", "Biotechnology and Its Applications", "Ecology and Environment"
            ]
        };

        const MOCK_FLASHCARDS = [
            { front: "What is the unit of Electric Field?", back: "Newton per Coulomb (N/C) or Volt per meter (V/m)" },
            { front: "Define Osmosis.", back: "Movement of solvent molecules from lower solute concentration to higher solute concentration through a semi-permeable membrane." },
            { front: "What is the general formula of Alkanes?", back: "CnH2n+2" },
            { front: "Who is known as the father of Genetics?", back: "Gregor Mendel" },
            { front: "What is the value of Universal Gravitational Constant (G)?", back: "6.674 × 10⁻¹¹ N·m²/kg²" }
        ];

        // --- API Helper ---
        const generateGeminiFlashcards = async (subject, chapters, level, count) => {
            const apiKey = ""; // Injected by environment
            
            // Fallback if no key or error
            if (!apiKey) {
                console.warn("No API Key found, using mock data.");
                return new Promise(resolve => setTimeout(() => resolve(MOCK_FLASHCARDS.slice(0, count)), 1500));
            }

            const prompt = `Generate ${count} flashcards for NEET (Indian Medical Entrance Exam).
            Subject: ${subject}
            Topics: ${chapters.join(', ')}
            Difficulty: ${level}
            
            Return ONLY a valid JSON array of objects. Each object must have exactly two keys: "front" (the question) and "back" (the answer).
            Do not include markdown code blocks. Just the raw JSON string.`;

            try {
                const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=${apiKey}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        contents: [{ parts: [{ text: prompt }] }]
                    })
                });

                const data = await response.json();
                let text = data.candidates?.[0]?.content?.parts?.[0]?.text;
                
                // Clean up markdown if present
                if (text.startsWith('```json')) text = text.replace('```json', '').replace('```', '');
                if (text.startsWith('```')) text = text.replace('```', '').replace('```', '');
                
                return JSON.parse(text);
            } catch (error) {
                console.error("API Error:", error);
                return MOCK_FLASHCARDS.slice(0, count);
            }
        };

        // --- Icons ---
        const { MessageCircle, BookOpen, User, Settings, Zap, Send, ChevronDown, Check, RotateCw, X, BrainCircuit, GraduationCap, Layout, ChevronLeft, ChevronRight, Layers } = lucide;

        // --- Components ---

        const MultiSelectDropdown = ({ options, selected, onChange, label }) => {
            const [isOpen, setIsOpen] = React.useState(false);
            const dropdownRef = React.useRef(null);

            React.useEffect(() => {
                const handleClickOutside = (event) => {
                    if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                        setIsOpen(false);
                    }
                };
                document.addEventListener('mousedown', handleClickOutside);
                return () => document.removeEventListener('mousedown', handleClickOutside);
            }, []);

            const toggleOption = (option) => {
                if (selected.includes(option)) {
                    onChange(selected.filter(item => item !== option));
                } else {
                    onChange([...selected, option]);
                }
            };

            return (
                <div className="relative" ref={dropdownRef}>
                    <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
                    <div 
                        onClick={() => setIsOpen(!isOpen)}
                        className="w-full bg-white border border-gray-300 rounded-lg px-4 py-2.5 text-sm cursor-pointer flex justify-between items-center hover:border-emerald-500 transition-colors shadow-sm"
                    >
                        <span className={`truncate ${selected.length === 0 ? 'text-gray-400' : 'text-gray-800'}`}>
                            {selected.length === 0 ? "Select Chapters..." : `${selected.length} Chapters Selected`}
                        </span>
                        <ChevronDown size={16} className={`text-gray-500 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
                    </div>

                    {isOpen && (
                        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-xl max-h-60 overflow-y-auto">
                            {options.map((option) => (
                                <div 
                                    key={option}
                                    onClick={() => toggleOption(option)}
                                    className="px-4 py-2.5 hover:bg-emerald-50 cursor-pointer flex items-center gap-3 transition-colors border-b border-gray-50 last:border-0"
                                >
                                    <div className={`w-4 h-4 rounded border flex items-center justify-center transition-colors ${selected.includes(option) ? 'bg-emerald-600 border-emerald-600' : 'border-gray-400'}`}>
                                        {selected.includes(option) && <Check size={10} className="text-white" />}
                                    </div>
                                    <span className="text-sm text-gray-700">{option}</span>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            );
        };

        const FlashcardViewer = ({ cards, onClose }) => {
            const [currentIndex, setCurrentIndex] = React.useState(0);
            const [isFlipped, setIsFlipped] = React.useState(false);

            if (!cards || cards.length === 0) return null;

            const nextCard = () => {
                if (currentIndex < cards.length - 1) {
                    setIsFlipped(false);
                    setTimeout(() => setCurrentIndex(c => c + 1), 150);
                }
            };

            const prevCard = () => {
                if (currentIndex > 0) {
                    setIsFlipped(false);
                    setTimeout(() => setCurrentIndex(c => c - 1), 150);
                }
            };

            return (
                <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
                    <div className="w-full max-w-2xl flex flex-col items-center">
                        {/* Header */}
                        <div className="w-full flex justify-between items-center mb-6 text-white">
                            <div className="flex items-center gap-2">
                                <Zap className="text-yellow-400 fill-yellow-400" size={24} />
                                <span className="text-xl font-bold tracking-wide">Study Mode</span>
                            </div>
                            <div className="flex items-center gap-4">
                                <span className="bg-white/10 px-3 py-1 rounded-full text-sm font-medium">
                                    {currentIndex + 1} / {cards.length}
                                </span>
                                <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-full transition-colors">
                                    <X size={24} />
                                </button>
                            </div>
                        </div>

                        {/* Card Scene */}
                        <div className="w-full aspect-[3/2] perspective-1000 group cursor-pointer" onClick={() => setIsFlipped(!isFlipped)}>
                            <div className={`relative w-full h-full duration-500 transform-style-3d transition-transform ${isFlipped ? 'rotate-y-180' : ''}`}>
                                
                                {/* Front */}
                                <div className="absolute w-full h-full bg-white rounded-2xl shadow-2xl backface-hidden flex flex-col items-center justify-center p-8 text-center border-b-4 border-emerald-500">
                                    <span className="absolute top-6 left-6 text-xs font-bold text-emerald-600 uppercase tracking-widest bg-emerald-100 px-3 py-1 rounded-full">Question</span>
                                    <p className="text-2xl md:text-3xl text-gray-800 font-medium leading-relaxed">
                                        {cards[currentIndex].front}
                                    </p>
                                    <div className="absolute bottom-6 text-gray-400 text-sm flex items-center gap-2">
                                        <RotateCw size={14} /> Click to flip
                                    </div>
                                </div>

                                {/* Back */}
                                <div className="absolute w-full h-full bg-emerald-600 rounded-2xl shadow-2xl backface-hidden rotate-y-180 flex flex-col items-center justify-center p-8 text-center text-white">
                                    <span className="absolute top-6 left-6 text-xs font-bold text-emerald-100 uppercase tracking-widest bg-emerald-700/50 px-3 py-1 rounded-full">Answer</span>
                                    <p className="text-xl md:text-2xl font-medium leading-relaxed">
                                        {cards[currentIndex].back}
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* Controls */}
                        <div className="flex items-center gap-6 mt-8">
                            <button 
                                onClick={prevCard} 
                                disabled={currentIndex === 0}
                                className="p-4 rounded-full bg-white text-emerald-900 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-emerald-50 hover:scale-110 transition-all shadow-lg"
                            >
                                <ChevronLeft size={24} />
                            </button>
                            <div className="text-white/80 text-sm font-medium">Use arrows to navigate</div>
                            <button 
                                onClick={nextCard} 
                                disabled={currentIndex === cards.length - 1}
                                className="p-4 rounded-full bg-white text-emerald-900 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-emerald-50 hover:scale-110 transition-all shadow-lg"
                            >
                                <ChevronRight size={24} />
                            </button>
                        </div>
                    </div>
                </div>
            );
        };

        const FlashcardGeneratorModal = ({ isOpen, onClose, onGenerate }) => {
            const [subject, setSubject] = React.useState('Physics');
            const [selectedChapters, setSelectedChapters] = React.useState([]);
            const [level, setLevel] = React.useState('Medium');
            const [quantity, setQuantity] = React.useState(5);
            const [isGenerating, setIsGenerating] = React.useState(false);

            if (!isOpen) return null;

            const handleSubjectChange = (e) => {
                setSubject(e.target.value);
                setSelectedChapters([]); // Reset chapters when subject changes
            };

            const handleGenerate = async () => {
                if (selectedChapters.length === 0) {
                    alert("Please select at least one chapter.");
                    return;
                }
                setIsGenerating(true);
                await onGenerate(subject, selectedChapters, level, quantity);
                setIsGenerating(false);
            };

            return (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4 animate-in fade-in duration-200">
                    <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden flex flex-col max-h-[90vh]">
                        {/* Header */}
                        <div className="px-6 py-5 bg-gradient-to-r from-emerald-600 to-teal-600 text-white flex justify-between items-center">
                            <div className="flex items-center gap-3">
                                <div className="p-2 bg-white/20 rounded-lg backdrop-blur-md">
                                    <BrainCircuit size={20} className="text-white" />
                                </div>
                                <div>
                                    <h2 className="text-lg font-bold">AI Flashcards</h2>
                                    <p className="text-emerald-100 text-xs">Generate custom study material instantly</p>
                                </div>
                            </div>
                            <button onClick={onClose} className="text-white/80 hover:text-white transition-colors">
                                <X size={20} />
                            </button>
                        </div>

                        {/* Body */}
                        <div className="p-6 space-y-5 overflow-y-auto">
                            {/* Subject Select */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
                                <select 
                                    value={subject} 
                                    onChange={handleSubjectChange}
                                    className="w-full bg-gray-50 border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all outline-none appearance-none"
                                >
                                    {Object.keys(NEET_SYLLABUS).map(sub => (
                                        <option key={sub} value={sub}>{sub}</option>
                                    ))}
                                </select>
                            </div>

                            {/* Chapter Select (Custom Multi-select) */}
                            <MultiSelectDropdown 
                                label="Chapters / Sub-topics" 
                                options={NEET_SYLLABUS[subject]} 
                                selected={selectedChapters} 
                                onChange={setSelectedChapters} 
                            />

                            {/* Difficulty & Quantity Grid */}
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Difficulty</label>
                                    <div className="flex bg-gray-100 p-1 rounded-lg">
                                        {['Easy', 'Medium', 'Hard'].map((l) => (
                                            <button
                                                key={l}
                                                onClick={() => setLevel(l)}
                                                className={`flex-1 py-1.5 text-xs font-medium rounded-md transition-all ${
                                                    level === l ? 'bg-white text-emerald-700 shadow-sm' : 'text-gray-500 hover:text-gray-700'
                                                }`}
                                            >
                                                {l}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Quantity</label>
                                    <div className="flex items-center border border-gray-300 rounded-lg overflow-hidden bg-white">
                                        <button 
                                            onClick={() => setQuantity(Math.max(1, quantity - 1))}
                                            className="px-3 py-2 bg-gray-50 border-r hover:bg-gray-100 text-gray-600"
                                        >-</button>
                                        <div className="flex-1 text-center text-sm font-medium text-gray-800">{quantity} Cards</div>
                                        <button 
                                            onClick={() => setQuantity(Math.min(20, quantity + 1))}
                                            className="px-3 py-2 bg-gray-50 border-l hover:bg-gray-100 text-gray-600"
                                        >+</button>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Footer */}
                        <div className="p-6 pt-2 bg-white">
                            <button 
                                onClick={handleGenerate} 
                                disabled={isGenerating}
                                className="w-full py-3 bg-emerald-600 hover:bg-emerald-700 active:bg-emerald-800 text-white font-semibold rounded-xl shadow-lg shadow-emerald-200 transition-all flex justify-center items-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed"
                            >
                                {isGenerating ? (
                                    <>
                                        <div className="loader border-white/30 border-t-white w-5 h-5"></div>
                                        <span>Designing Cards...</span>
                                    </>
                                ) : (
                                    <>
                                        <Zap size={18} />
                                        <span>Generate Flashcards</span>
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            );
        };

        const ChatInterface = () => {
            const [messages, setMessages] = React.useState([
                { id: 1, sender: 'bot', text: "Hello! I'm your NEETx AI Assistant. How can I help you with your preparation today?" }
            ]);
            const [inputText, setInputText] = React.useState("");
            const [showFlashcardModal, setShowFlashcardModal] = React.useState(false);
            const [generatedCards, setGeneratedCards] = React.useState(null);
            
            const chatEndRef = React.useRef(null);

            React.useEffect(() => {
                chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
            }, [messages]);

            const handleSend = () => {
                if (!inputText.trim()) return;
                
                const newMsg = { id: Date.now(), sender: 'user', text: inputText };
                setMessages(prev => [...prev, newMsg]);
                setInputText("");

                // Mock bot response
                setTimeout(() => {
                    const botMsg = { id: Date.now() + 1, sender: 'bot', text: "I've received your query. Is there anything specific from the syllabus you'd like to explore?" };
                    setMessages(prev => [...prev, botMsg]);
                }, 1000);
            };

            const handleGenerateFlashcards = async (subject, chapters, level, count) => {
                // Generate cards
                const cards = await generateGeminiFlashcards(subject, chapters, level, count);
                setShowFlashcardModal(false);
                setGeneratedCards(cards);
                
                // Add a message about it
                setMessages(prev => [...prev, { 
                    id: Date.now(), 
                    sender: 'bot', 
                    text: `I've generated ${count} ${level} flashcards for ${subject} (${chapters.length} topics).`,
                    isSystem: true
                }]);
            };

            return (
                <div className="flex-1 flex flex-col h-full bg-slate-50 relative overflow-hidden">
                    {/* Header */}
                    <div className="bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center shadow-sm z-10">
                        <div>
                            <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                                <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                                AI Study Assistant
                            </h2>
                            <p className="text-sm text-gray-500">Online | NEET Expert Model</p>
                        </div>
                        <div className="flex gap-2">
                            <button className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg transition-colors">
                                <Settings size={20} />
                            </button>
                        </div>
                    </div>

                    {/* Messages Area */}
                    <div className="flex-1 overflow-y-auto p-6 space-y-6">
                        {messages.map((msg) => (
                            <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                                <div className={`max-w-[80%] rounded-2xl px-5 py-3 shadow-sm ${
                                    msg.sender === 'user' 
                                        ? 'bg-emerald-600 text-white rounded-br-none' 
                                        : 'bg-white border border-gray-100 text-gray-700 rounded-bl-none'
                                }`}>
                                    <p className="leading-relaxed text-sm md:text-base">{msg.text}</p>
                                </div>
                            </div>
                        ))}
                        <div ref={chatEndRef} />
                    </div>

                    {/* Input Area & Tools */}
                    <div className="p-4 bg-white border-t border-gray-200 z-20">
                        {/* Quick Tools */}
                        <div className="flex gap-2 mb-3 overflow-x-auto pb-2 scrollbar-hide">
                            <button 
                                onClick={() => setShowFlashcardModal(true)}
                                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-teal-50 to-emerald-50 text-emerald-700 rounded-full border border-emerald-200 hover:border-emerald-400 hover:shadow-md transition-all text-sm font-medium whitespace-nowrap group"
                            >
                                <div className="bg-white p-1 rounded-full shadow-sm group-hover:scale-110 transition-transform">
                                    <Zap size={14} className="fill-emerald-500 text-emerald-500" />
                                </div>
                                AI Flashcards
                            </button>
                             <button className="flex items-center gap-2 px-4 py-2 bg-gray-50 text-gray-600 rounded-full border border-gray-200 hover:bg-gray-100 transition-all text-sm font-medium whitespace-nowrap">
                                <Layout size={14} /> Summarize
                            </button>
                            <button className="flex items-center gap-2 px-4 py-2 bg-gray-50 text-gray-600 rounded-full border border-gray-200 hover:bg-gray-100 transition-all text-sm font-medium whitespace-nowrap">
                                <BookOpen size={14} /> Quiz Me
                            </button>
                        </div>

                        {/* Input Box */}
                        <div className="flex items-center gap-2 bg-gray-100 rounded-xl px-4 py-2 border border-transparent focus-within:border-emerald-500 focus-within:ring-2 focus-within:ring-emerald-100 transition-all">
                            <input 
                                type="text" 
                                className="flex-1 bg-transparent border-none outline-none text-gray-700 placeholder-gray-400 py-2"
                                placeholder="Ask a doubt or request a topic..."
                                value={inputText}
                                onChange={(e) => setInputText(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                            />
                            <button 
                                onClick={handleSend}
                                className={`p-2 rounded-lg transition-all ${inputText.trim() ? 'bg-emerald-600 text-white shadow-md hover:bg-emerald-700' : 'bg-gray-200 text-gray-400'}`}
                            >
                                <Send size={18} />
                            </button>
                        </div>
                    </div>

                    {/* Modals */}
                    <FlashcardGeneratorModal 
                        isOpen={showFlashcardModal} 
                        onClose={() => setShowFlashcardModal(false)} 
                        onGenerate={handleGenerateFlashcards}
                    />

                    {generatedCards && (
                        <FlashcardViewer 
                            cards={generatedCards} 
                            onClose={() => setGeneratedCards(null)} 
                        />
                    )}
                </div>
            );
        };

        const Sidebar = () => {
            const menuItems = [
                { icon: Layout, label: 'Dashboard', active: false },
                { icon: MessageCircle, label: 'AI Chat', active: true },
                { icon: BookOpen, label: 'Courses', active: false },
                { icon: Layers, label: 'Practice', active: false },
                { icon: GraduationCap, label: 'Mock Tests', active: false },
            ];

            return (
                <div className="w-20 md:w-64 bg-white border-r border-gray-200 flex flex-col justify-between h-full hidden md:flex">
                    <div>
                        <div className="p-6 flex items-center gap-3">
                            <div className="w-8 h-8 bg-emerald-600 rounded-lg flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-emerald-200">
                                N
                            </div>
                            <span className="text-2xl font-bold bg-gradient-to-r from-emerald-800 to-teal-600 bg-clip-text text-transparent hidden md:block">
                                NEETx
                            </span>
                        </div>

                        <nav className="mt-6 px-4 space-y-1">
                            {menuItems.map((item, idx) => (
                                <a 
                                    key={idx}
                                    href="#" 
                                    className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                                        item.active 
                                            ? 'bg-emerald-50 text-emerald-700 font-medium' 
                                            : 'text-gray-500 hover:bg-gray-50 hover:text-gray-700'
                                    }`}
                                >
                                    <item.icon size={20} />
                                    <span className="hidden md:block">{item.label}</span>
                                </a>
                            ))}
                        </nav>
                    </div>

                    <div className="p-4 border-t border-gray-100">
                        <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-gray-50 hover:bg-gray-100 transition-colors cursor-pointer">
                            <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 font-bold">
                                S
                            </div>
                            <div className="hidden md:block overflow-hidden">
                                <p className="text-sm font-medium text-gray-700 truncate">Student User</p>
                                <p className="text-xs text-gray-500 truncate">Pro Plan</p>
                            </div>
                        </div>
                    </div>
                </div>
            );
        };

        const App = () => {
            return (
                <div className="flex h-screen w-full bg-white overflow-hidden">
                    <Sidebar />
                    <ChatInterface />
                </div>
            );
        };

        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<App />);
    </script>
</body>
</html>
