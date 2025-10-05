import { useState, useEffect } from "react";
import { HeroSection } from "./components/HeroSection";
import { ResultsSection } from "./components/ResultsSection";
import { Header } from "./components/Header";

export default function App() {
  const [hasResult, setHasResult] = useState(false);
  const [inputValue, setInputValue] = useState("");
  const [analysisData, setAnalysisData] = useState<any>(null);
  const [isDark, setIsDark] = useState(true);

  const API_BASE_URL = "http://127.0.0.1:8000";
  // Initialize theme on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const shouldBeDark = savedTheme ? savedTheme === 'dark' : prefersDark;
    
    setIsDark(shouldBeDark);
    if (shouldBeDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, []);

  const toggleTheme = () => {
    const newTheme = !isDark;
    setIsDark(newTheme);
    
    if (newTheme) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  };

  const handleAnalyze = async (input: string | File, type: string) => {
    // setInputValue(input); // Can't set File object as string
    // setError(null);

    let endpoint = "";
    let body: any;
    const headers: any = {};

    switch (type) {
      case "text":
        endpoint = `${API_BASE_URL}/api/v1/analysis`;
        headers["Content-Type"] = "application/json";
        body = JSON.stringify({ text: input });
        break;
      case "url":
        endpoint = `${API_BASE_URL}/api/v1/analyze-url`;
        headers["Content-Type"] = "application/json";
        body = JSON.stringify({ url: input });
        break;
      case "image":
      case "voice":
        endpoint = type === 'image' ? `${API_BASE_URL}/api/v1/analyze-image` : `${API_BASE_URL}/api/v1/analyze-voice`;
        if (!(input instanceof File)) {
          console.error("A file is required for image/voice analysis");
          return;
        }
        const formData = new FormData();
        formData.append("file", input);
        body = formData;
        // For multipart/form-data, the browser sets the Content-Type header automatically with the correct boundary
        break;
      default:
        console.error("Invalid analysis type");
        return;
    }
    
    try {
      console.log('Sending request to:', endpoint);
      // Call your backend API
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          ...headers,
          'Accept': 'application/json',
        },
        body: body,
        mode: 'cors',
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Server response:', errorText);
        throw new Error(`Server error: ${response.status} - ${errorText}`);
      }

      const data = await response.json();
      
      // Transform backend response to match your frontend structure
      // const transformedData = {
      //   query: data.query || (typeof input === 'string' ? input : 'Uploaded file'),
      //   confidence: typeof data.confidence === 'number' ? data.confidence : 0,
      //   isFake: Boolean(data.isFake || data.is_fake),
      //   highlightedQuery: Array.isArray(data.highlightedQuery || data.highlighted_query) 
      //     ? (data.highlightedQuery || data.highlighted_query) 
      //     : undefined,
      //   explanation: {
      //     verdict: data.explanation?.verdict || data.verdict || "Unknown",
      //     reasons: Array.isArray(data.explanation?.reasons || data.reasons) 
      //       ? (data.explanation?.reasons || data.reasons) 
      //       : undefined
      //   },
      //   relatedArticles: Array.isArray(data.relatedArticles || data.related_articles) 
      //     ? (data.relatedArticles || data.related_articles) 
      //     : undefined
      // };

      const transformedData = {
        query: data.extracted_text || (typeof input === 'string' ? input : 'Uploaded file'),
        confidence: data.analysis?.confidence ?? 0,
        isFake: data.analysis?.verdict === "Fake", // Determine isFake from the verdict
        highlightedQuery: data.analysis?.highlighted ?? [], // Use highlighted from the analysis object
        explanation: {
          verdict: data.analysis?.verdict || "Error",
          // The backend sends a single explanation string, so we'll wrap it in an array for the frontend
          reasons: data.analysis?.explanation ? [data.analysis.explanation] : ["No explanation provided."], 
        },
        // Map 'related_sources' to 'relatedArticles'
        relatedArticles: (data.related_sources ?? []).flatMap((source: any) => 
          (source.data ?? []).map((post: any) => ({
            title: post.text,
            source: post.source,
            url: post.url,
          }))
        )
      };
      
      setAnalysisData(transformedData);
      setHasResult(true);
    } catch (error) {
      const err = error as Error;
      console.error('Analysis error:', err);
      // Set a user-friendly error message
      setAnalysisData({
        query: typeof input === 'string' ? input : 'File analysis',
        confidence: 0,
        isFake: false,
        highlightedQuery: [],
        explanation: {
          verdict: "Error",
        },
        relatedArticles: []
      });
      setHasResult(true);
    }
    // } finally {
    //   setIsLoading(false);
    // }
  };

  const handleReset = () => {
    setHasResult(false);
    setInputValue("");
    setAnalysisData(null);
  };

  //   //Mock analysis results
  //   const mockData = {
  //     query: input || "Breaking: Scientists discover that drinking 10 cups of coffee daily increases lifespan by 50 years! Click here to learn more about this miracle discovery that doctors don't want you to know!",
  //     confidence: 89,
  //     isFake: true,
  //     highlightedQuery: [
  //       { text: "Breaking: Scientists discover that drinking 10 cups of coffee daily ", isSuspicious: false },
  //       { text: "increases lifespan by 50 years!", isSuspicious: true },
  //       { text: " Click here to learn more about this ", isSuspicious: false },
  //       { text: "miracle discovery that doctors don't want you to know!", isSuspicious: true }
  //     ],
  //     explanation: {
  //       verdict: "Likely False",
  //       reasons: [
  //         "Sensationalist language commonly used in clickbait articles",
  //         "Lacks credible source citations or peer-reviewed research",
  //         "Uses emotional manipulation phrases like 'doctors don't want you to know'",
  //         "Extraordinary claims without proportional evidence"
  //       ]
  //     },
  //     relatedArticles: [
  //       {
  //         title: "The Truth About Coffee and Longevity: What Science Really Says",
  //         source: "National Health Institute",
  //         url: "#"
  //       },
  //       {
  //         title: "How to Identify Clickbait Health Claims Online",
  //         source: "Digital Literacy Foundation",
  //         url: "#"
  //       },
  //       {
  //         title: "Coffee Consumption: Benefits and Risks According to Research",
  //         source: "Journal of Medical Studies",
  //         url: "#"
  //       }
  //     ]
  //   };

  //   setAnalysisData(mockData);
  //   setHasResult(true);
  // };

  // const handleReset = () => {
  //   setHasResult(false);
  //   setInputValue("");
  //   setAnalysisData(null);
  //

  return (
        <div className="min-h-screen w-full relative overflow-hidden">
      {/* Soft Blue Radial Background */}
      <div
        className="absolute inset-0 z-0 transition-colors duration-300"
        style={{
          background: isDark ? "#0a0a0f" : "#ffffff",
          backgroundImage: isDark
            ? `radial-gradient(circle at top center, rgba(59, 130, 246, 0.3), transparent 70%)`
            : `radial-gradient(circle at top center, rgba(59, 130, 246, 0.5), transparent 70%)`,
        }}
      />
    <div className={`min-h-screen transition-colors duration-200 ${
      isDark 
        ? 'bg-gradient-to-b from-[#0a0a0f] via-[#0f0f1a] to-[#1a1a2e] text-white' 
        : 'bg-gradient-to-b from-gray-50 via-white to-gray-100 text-gray-900'
    }`}>
      <Header isDark={isDark} onThemeToggle={toggleTheme} />
      
      <div className="max-w-5xl mx-auto px-6 py-8 pt-24">
        {!hasResult ? (
          <HeroSection onAnalyze={handleAnalyze} />
        ) : (
          <ResultsSection data={analysisData} onReset={handleReset} />
        )}
      </div>
    </div>
    </div>
  );
}