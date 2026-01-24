import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import ReactDiffViewer, { DiffMethod } from 'react-diff-viewer-continued';
import { Copy, Check, Split, Code2, Columns, Rows } from "lucide-react";
import { useState } from "react";

interface CodeBlockProps {
    code: string;
    originalCode?: string;
    fileName?: string;
}

export function CodeBlock({ code, originalCode, fileName = "Python Source" }: CodeBlockProps) {
    const [copied, setCopied] = useState(false);
    const [showDiff, setShowDiff] = useState(!!originalCode);
    const [isSplitView, setIsSplitView] = useState(false);

    const handleCopy = () => {
        navigator.clipboard.writeText(code);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const diffStyles = {
        variables: {
            dark: {
                diffViewerBackground: '#0d1117',
                diffViewerColor: '#e6edf3',
                addedBackground: '#1f6feb26',
                addedColor: '#e6edf3',
                removedBackground: '#da363326',
                removedColor: '#e6edf3',
                wordAddedBackground: '#1f6feb66',
                wordRemovedBackground: '#da363366',
                addedGutterBackground: '#1f6feb1a',
                removedGutterBackground: '#da36331a',
                gutterBackground: '#0d1117',
                gutterBackgroundDark: '#0d1117',
                highlightBackground: '#2a3967',
                highlightGutterBackground: '#2d4077',
                codeFoldGutterBackground: '#21232b',
                codeFoldBackground: '#262831',
                emptyLineBackground: '#0d1117',
                gutterColor: '#464c67',
                addedGutterColor: '#8c8c8c',
                removedGutterColor: '#8c8c8c',
                codeFoldContentColor: '#555a7b',
                diffViewerTitleBackground: '#2f323e',
                diffViewerTitleColor: '#555a7b',
                diffViewerTitleBorderColor: '#353846',
            }
        },
        line: {
            padding: '2px 0',
            fontSize: '12px',
            lineHeight: '1.5',
            fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
        },
        content: {
            padding: '0 4px',
        },
        gutter: {
            padding: '0 8px',
            minWidth: '30px',
        }
    };

    return (
        <div className="relative group rounded border border-blue-900/30 overflow-hidden bg-[#0d1117]">
            <div className="flex items-center justify-between px-3 py-1.5 bg-blue-900/10 border-b border-blue-900/30">
                <div className="flex gap-1.5">
                    <div className="w-2 h-2 rounded-full bg-red-500/20 border border-red-500/50" />
                    <div className="w-2 h-2 rounded-full bg-yellow-500/20 border border-yellow-500/50" />
                    <div className="w-2 h-2 rounded-full bg-green-500/20 border border-green-500/50" />
                </div>
                <div className="text-[10px] font-mono text-blue-500/50 uppercase tracking-wider">
                    {fileName}
                </div>
                <div className="flex items-center gap-2">
                    {originalCode && showDiff && (
                        <button
                            onClick={() => setIsSplitView(!isSplitView)}
                            className="p-1 hover:bg-blue-500/10 rounded text-blue-400/50 hover:text-blue-400 transition-colors"
                            title={isSplitView ? "Switch to Unified View" : "Switch to Split View"}
                        >
                            {isSplitView ? <Rows className="w-3 h-3" /> : <Columns className="w-3 h-3" />}
                        </button>
                    )}
                    {originalCode && (
                        <button
                            onClick={() => setShowDiff(!showDiff)}
                            className="p-1 hover:bg-blue-500/10 rounded text-blue-400/50 hover:text-blue-400 transition-colors"
                            title={showDiff ? "Show Code Only" : "Show Diff"}
                        >
                            {showDiff ? <Code2 className="w-3 h-3" /> : <Split className="w-3 h-3" />}
                        </button>
                    )}
                    <button 
                        onClick={handleCopy}
                        className="p-1 hover:bg-blue-500/10 rounded text-blue-400/50 hover:text-blue-400 transition-colors"
                        title="Copy Code"
                    >
                        {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                    </button>
                </div>
            </div>
            
            {showDiff && originalCode ? (
                <div className="text-xs font-mono overflow-x-auto max-h-[500px] overflow-y-auto custom-scrollbar">
                    <ReactDiffViewer 
                        oldValue={originalCode} 
                        newValue={code} 
                        splitView={isSplitView} 
                        useDarkTheme={true}
                        styles={diffStyles}
                        compareMethod={DiffMethod.WORDS}
                    />
                </div>
            ) : (
                <SyntaxHighlighter 
                    language="python" 
                    style={vscDarkPlus}
                    customStyle={{
                        margin: 0,
                        padding: '1rem',
                        fontSize: '0.75rem',
                        backgroundColor: 'transparent',
                    }}
                >
                    {code}
                </SyntaxHighlighter>
            )}
        </div>
    );
}
