import { useEffect, useRef } from "react";
import { AgentEvent } from "@/app/page";
import { Activity } from "lucide-react";
import { EventCard } from "./EventCard";
import { CodeBlock } from "./CodeBlock";
import { AnimatePresence, motion } from "framer-motion";

interface TimelineProps {
    events: AgentEvent[];
    processing: boolean;
    originalCode?: string;
}

export function Timeline({ events, processing, originalCode }: TimelineProps) {
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [events]);

    return (
        <div className="flex-1 overflow-y-auto p-6 space-y-6 relative" ref={scrollRef}>
            {events.length === 0 && !processing && (
                <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-500 pointer-events-none">
                    <div className="w-32 h-32 border border-blue-500/20 rounded-full flex items-center justify-center mb-6 relative">
                        <div className="absolute inset-0 rounded-full border border-blue-500/10 animate-[spin_10s_linear_infinite]" />
                        <div className="absolute inset-2 rounded-full border border-blue-500/10 animate-[spin_15s_linear_infinite_reverse]" />
                        <Activity className="w-12 h-12 text-blue-500/50 animate-pulse" />
                        <div className="absolute -bottom-8 text-[10px] font-mono text-blue-500/50 tracking-[0.3em] uppercase">
                            System Standby
                        </div>
                    </div>
                    <p className="text-lg font-mono text-blue-400/80 tracking-widest uppercase">Awaiting Input</p>
                    <p className="text-xs font-mono text-slate-600 mt-2">Initialize protocol via sidebar module</p>
                </div>
            )}

            <AnimatePresence mode="popLayout">
                {events.map((event, index) => (
                    <motion.div
                        key={index}
                        initial={{ opacity: 0, y: 20, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        transition={{ duration: 0.3, delay: index * 0.05 }}
                    >
                        <EventCard event={event} originalCode={originalCode} />
                    </motion.div>
                ))}
            </AnimatePresence>

            {processing && (
                <motion.div 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="pl-8 relative"
                >
                    <div className="absolute left-[-5px] top-1 w-2 h-2 bg-slate-600 rounded-full animate-ping"></div>
                    <div className="text-xs text-slate-500 font-mono typing-cursor">Agents are thinking...</div>
                </motion.div>
            )}
        </div>
    );
}
