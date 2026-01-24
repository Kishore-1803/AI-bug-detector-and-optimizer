"use client";

import { useState, useRef, useEffect } from "react";
import { Header } from "@/components/Header";
import { Sidebar } from "@/components/Sidebar";
import { Timeline } from "@/components/Timeline";
import { AnimatePresence, motion } from "framer-motion";

import { CodeBlock } from "@/components/CodeBlock";
import { Code2 } from "lucide-react";

export type AgentEvent = {
  agent: string;
  message: string;
  metadata?: any;
};

export default function Home() {
  const [mode, setMode] = useState<"fix" | "optimize" | "security">("fix");
  const [inputCode, setInputCode] = useState('def add(a, b):\n    return a - b  # Bug: subtraction instead of addition');
  const [bugDescription, setBugDescription] = useState('The add function returns the wrong result. It seems to subtract instead of add.');
  const [testInput, setTestInput] = useState('');
  const [language, setLanguage] = useState('python');
  const [complexityData, setComplexityData] = useState<{
      origTime?: string;
      origSpace?: string;
      optTime?: string;
      optSpace?: string;
  }>({});
  const [processing, setProcessing] = useState(false);
  const [events, setEvents] = useState<AgentEvent[]>([]);

  const startProcess = async () => {
    setProcessing(true);
    setEvents([]);
    setComplexityData({});

    let endpoint = 'http://localhost:8000/analyze/fix';
    if (mode === 'optimize') endpoint = 'http://localhost:8000/analyze/optimize';
    if (mode === 'security') endpoint = 'http://localhost:8000/analyze/security';
    
    let payload = {};
    if (mode === 'fix') {
        payload = { description: bugDescription, code: inputCode };
    } else if (mode === 'optimize') {
        payload = { code: inputCode, test_input: testInput, language: language };
    } else if (mode === 'security') {
        payload = { code: inputCode };
    }

    console.log("Sending payload:", payload);

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.body) throw new Error("No response body");

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value);
            const lines = chunk.split('\n').filter(line => line.trim());
            
            for (const line of lines) {
                try {
                    const data = JSON.parse(line);
                    processEvent(data);
                } catch (e) {
                    console.error("Error parsing JSON", e);
                }
            }
        }
    } catch (error: any) {
        console.error("Error:", error);
        setEvents(prev => [...prev, {
            agent: 'System Error',
            message: 'Connection failed: ' + error.message,
            metadata: { error: error }
        }]);
    } finally {
        setProcessing(false);
    }
  };

  const processEvent = (data: any) => {
    let newEvent: AgentEvent | null = null;
    let newCode: string | null = null;

    if (data.developer) {
        newCode = data.developer.current_patch || data.developer.current_optimized_code;
        newEvent = {
            agent: 'Developer',
            message: data.developer.developer_thought || "Generating code patch...",
            metadata: { 
                code: newCode
            }
        };
    } else if (data.security_engineer) {
        newCode = data.security_engineer.current_patch;
        newEvent = {
            agent: 'Security Engineer',
            message: data.security_engineer.security_thought || "Auditing code for vulnerabilities...",
            metadata: { 
                code: newCode,
                vulnerabilities: data.security_engineer.vulnerabilities
            }
        };
    } else if (data.optimizer) {
        // Update complexity data state
        if (data.optimizer.original_time_complexity) {
            setComplexityData({
                origTime: data.optimizer.original_time_complexity,
                origSpace: data.optimizer.original_space_complexity,
                optTime: data.optimizer.optimized_time_complexity,
                optSpace: data.optimizer.optimized_space_complexity
            });
        }
        
        newCode = data.optimizer.current_optimized_code;
        newEvent = {
            agent: 'Optimizer',
            message: data.optimizer.optimizer_thought || "Optimizing code...",
            metadata: { 
                code: newCode
            }
        };
    } else if (data.critic) {
        newEvent = {
            agent: 'Critic',
            message: data.critic.critique_feedback || "Reviewing code...",
            metadata: { 
                status: data.critic.status 
            }
        };
    } else if (data.tester) {
        newEvent = {
            agent: 'Tester',
            message: data.tester.test_feedback || "Running tests...",
            metadata: { 
                status: data.tester.status 
            }
        };
    } else if (data.benchmarker) {
        newEvent = {
            agent: 'Benchmarker',
            message: data.benchmarker.benchmark_feedback || "Benchmarking performance...",
            metadata: { 
                stats: data.benchmarker.benchmark_results 
            }
        };
    } else if (data.optimization_critic) {
         newEvent = {
            agent: 'Optimization Critic',
            message: data.optimization_critic.critique_feedback,
            metadata: {
                status: data.optimization_critic.status
            }
        };
    } else if (data.error) {
        newEvent = {
            agent: 'Error',
            message: data.error.payload || "An unknown error occurred",
        };
    }

    if (newEvent) {
        setEvents(prev => [...prev, newEvent!]);
    }
  };

  const latestCode = events.slice().reverse().find(e => e.metadata?.code)?.metadata?.code;
  const latestCodeAgent = events.slice().reverse().find(e => e.metadata?.code)?.agent;

  return (
    <main className="flex flex-col h-full relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 -z-10 bg-[#05050a]">
        <div className="absolute inset-0 bg-[linear-gradient(rgba(18,18,27,0.8)_1px,transparent_1px),linear-gradient(90deg,rgba(18,18,27,0.8)_1px,transparent_1px)] bg-[size:40px_40px] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_50%,#000_70%,transparent_100%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_800px_at_50%_200px,rgba(29,78,216,0.15),transparent)]" />
        <div className="scanlines" />
      </div>

      <Header mode={mode} setMode={setMode} />
      
      <div className="flex-1 flex overflow-hidden p-6 gap-6">
        <div className="w-[30%] h-full flex flex-col">
            <Sidebar 
                mode={mode}
                inputCode={inputCode}
                setInputCode={setInputCode}
                bugDescription={bugDescription}
                setBugDescription={setBugDescription}
                testInput={testInput}
                setTestInput={setTestInput}
                startProcess={startProcess}
                processing={processing}
                language={language}
                setLanguage={setLanguage}
                complexityData={complexityData}
            />
        </div>
        
        <div className="w-[30%] h-full hud-panel rounded-xl relative flex flex-col overflow-hidden">
            <div className="absolute top-0 left-0 px-4 py-1 bg-blue-500/10 border-b border-r border-blue-500/30 text-[10px] font-mono text-blue-400 uppercase tracking-widest">
                Live Feed // Secure Channel
            </div>
            <Timeline events={events} processing={processing} originalCode={inputCode} />
        </div>

        <div className="flex-1 h-full hud-panel rounded-xl relative flex flex-col overflow-hidden">
            <div className="absolute top-0 right-0 px-4 py-1 bg-green-500/10 border-b border-l border-green-500/30 text-[10px] font-mono text-green-400 uppercase tracking-widest">
                Output Module // Generated Code
            </div>
            {latestCode ? (
                <div className="flex-1 overflow-auto p-4 pt-10">
                    <div className="flex items-center gap-2 mb-2 text-xs font-mono text-slate-400">
                        <Code2 className="w-4 h-4 text-green-500" /> 
                        <span>Generated by {latestCodeAgent}</span>
                    </div>
                    <CodeBlock 
                        code={latestCode} 
                        originalCode={inputCode}
                        fileName={latestCodeAgent === 'Optimizer' ? 'Optimized Code' : 'Proposed Fix'}
                    />
                </div>
            ) : (
                <div className="flex-1 flex flex-col items-center justify-center text-slate-600 font-mono text-xs uppercase tracking-widest gap-2">
                    <div className="w-12 h-12 rounded-full border border-slate-800 flex items-center justify-center">
                        <Code2 className="w-6 h-6 opacity-20" />
                    </div>
                    Waiting for code generation...
                </div>
            )}
        </div>
      </div>
    </main>
  );
}
