import { Bug, Zap, Cpu, Activity, ShieldCheck } from "lucide-react";
import { clsx } from "clsx";

interface HeaderProps {
    mode: "fix" | "optimize" | "security";
    setMode: (mode: "fix" | "optimize" | "security") => void;
}

export function Header({ mode, setMode }: HeaderProps) {
    return (
        <header className="h-14 bg-[#0a0a12] border-b border-blue-900/30 flex items-center justify-between px-6 z-20 relative shadow-[0_0_20px_rgba(0,0,0,0.5)]">
            <div className="flex items-center gap-4">
                <div className="w-8 h-8 bg-blue-600/20 border border-blue-500/50 rounded flex items-center justify-center shadow-[0_0_10px_rgba(37,99,235,0.3)]">
                    <Cpu className="text-blue-400 w-5 h-5" />
                </div>
                <div className="flex flex-col">
                    <h1 className="text-lg font-bold text-white tracking-widest uppercase font-mono">
                        Agentic Code Studio
                    </h1>
                    <span className="text-[10px] text-blue-500/70 font-mono tracking-[0.2em]">V.2.0.4 // NEURAL LINK ACTIVE</span>
                </div>
            </div>
            
            <div className="flex bg-black/40 p-1 rounded border border-blue-900/30">
                <button 
                    onClick={() => setMode('fix')}
                    className={clsx(
                        'px-4 py-1.5 rounded text-xs font-bold uppercase tracking-wider transition-all duration-200 flex items-center gap-2 font-mono',
                        mode === 'fix' ? 'bg-blue-600/20 text-blue-400 border border-blue-500/50 shadow-[0_0_10px_rgba(37,99,235,0.2)]' : 'text-slate-500 hover:text-blue-400 hover:bg-blue-900/10'
                    )}
                >
                    <Bug className="w-3 h-3" /> Debug Protocol
                </button>
                <button 
                    onClick={() => setMode('optimize')}
                    className={clsx(
                        'px-4 py-1.5 rounded text-xs font-bold uppercase tracking-wider transition-all duration-200 flex items-center gap-2 font-mono',
                        mode === 'optimize' ? 'bg-purple-600/20 text-purple-400 border border-purple-500/50 shadow-[0_0_10px_rgba(147,51,234,0.2)]' : 'text-slate-500 hover:text-purple-400 hover:bg-purple-900/10'
                    )}
                >
                    <Zap className="w-3 h-3" /> Optimization
                </button>
                <button 
                    onClick={() => setMode('security')}
                    className={clsx(
                        'px-4 py-1.5 rounded text-xs font-bold uppercase tracking-wider transition-all duration-200 flex items-center gap-2 font-mono',
                        mode === 'security' ? 'bg-orange-600/20 text-orange-400 border border-orange-500/50 shadow-[0_0_10px_rgba(249,115,22,0.2)]' : 'text-slate-500 hover:text-orange-400 hover:bg-orange-900/10'
                    )}
                >
                    <ShieldCheck className="w-3 h-3" /> Security
                </button>
            </div>

            <div className="flex items-center gap-4">
                <div className="flex items-center gap-2 text-[10px] text-green-400 bg-green-900/10 px-3 py-1.5 rounded border border-green-500/20 font-mono uppercase tracking-wider">
                    <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse shadow-[0_0_5px_#22c55e]"></span>
                    System Online
                </div>
            </div>
        </header>
    );
}
