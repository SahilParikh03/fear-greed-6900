import { useRef, useEffect, useState } from "react";
import { motion, useScroll, useSpring, useTransform, AnimatePresence } from "framer-motion";
import { Activity, TrendingUp, Shield, Terminal, Zap, Twitter } from "lucide-react";
import { useNavigate } from "react-router-dom";

interface LivePrices {
  btc: number | null;
  eth: number | null;
  sol: number | null;
}

interface AgentSignal {
  index_score: number;
  sentiment: string;
  recommendation: string;
  is_volatile: boolean;
  timestamp: string;
}

// Tab content animation variants
const tabContentVariants = {
  enter: {
    opacity: 0,
    x: 0,
    transition: {
      duration: 0.25,
      ease: "easeOut",
    },
  },
  center: {
    opacity: 1,
    x: 0,
    transition: {
      duration: 0.25,
      ease: "easeOut",
    },
  },
  exit: {
    opacity: 0,
    x: 0,
    transition: {
      duration: 0.2,
      ease: "easeIn",
    },
  },
};

export function LandingPage() {
  const navigate = useNavigate();
  const containerRef = useRef<HTMLDivElement>(null);
  const [livePrices, setLivePrices] = useState<LivePrices>({ btc: null, eth: null, sol: null });
  const [sentimentScore, setSentimentScore] = useState<number>(65);
  const [activeTab, setActiveTab] = useState<"signal" | "insights">("signal");
  const [agentSignal, setAgentSignal] = useState<AgentSignal | null>(null);
  const [isTransitioning, setIsTransitioning] = useState(false);

  // Scroll progress tracking
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end start"],
  });

  // Smooth spring animation for scroll
  const scrollSpring = useSpring(scrollYProgress, {
    stiffness: 100,
    damping: 30,
    restDelta: 0.001,
  });

  // Transform values for portal effect
  const heroScale = useTransform(scrollSpring, [0, 1], [1, 2]);
  const heroOpacity = useTransform(scrollSpring, [0, 0.5], [1, 0]);
  const dashboardScale = useTransform(scrollSpring, [0, 1], [1.5, 1]);
  const dashboardOpacity = useTransform(scrollSpring, [0.3, 0.8], [0, 1]);
  const dashboardY = useTransform(scrollSpring, [0, 1], [100, 0]);

  // Connect to real-time price updates
  useEffect(() => {
    const eventSource = new EventSource("http://localhost:8000/api/v1/stream");

    eventSource.addEventListener("price", (event) => {
      try {
        const priceData = JSON.parse(event.data);
        setLivePrices((prev) => ({
          ...prev,
          [priceData.asset.toLowerCase()]: priceData.price,
        }));
      } catch (err) {
        console.error("Failed to parse price event:", err);
      }
    });

    return () => {
      eventSource.close();
    };
  }, []);

  // Simulate sentiment fluctuation
  useEffect(() => {
    const interval = setInterval(() => {
      setSentimentScore((prev) => {
        const change = (Math.random() - 0.5) * 10;
        return Math.max(0, Math.min(100, prev + change));
      });
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  // Fetch agent signal data
  useEffect(() => {
    const fetchAgentSignal = async () => {
      try {
        const response = await fetch("http://localhost:8000/api/v1/agent/signal", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            agent_id: "moltbot_v1",
            query: "analyze current market sentiment",
          }),
        });
        const data = await response.json();
        setAgentSignal(data);
      } catch (err) {
        console.error("Failed to fetch agent signal:", err);
        // Set fallback data for demo
        setAgentSignal({
          index_score: 32,
          sentiment: "FEAR",
          recommendation: "ACCUMULATE_BTC",
          is_volatile: false,
          timestamp: new Date().toISOString(),
        });
      }
    };

    fetchAgentSignal();
    // Refresh every 30 seconds
    const interval = setInterval(fetchAgentSignal, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleDiveIn = () => {
    // Smooth scroll to trigger animation
    window.scrollTo({
      top: window.innerHeight * 1.5,
      behavior: "smooth",
    });

    // Navigate after animation
    setTimeout(() => {
      navigate("/dashboard");
    }, 1500);
  };

  const handleLaunchDashboard = () => {
    // Only trigger animation if we're on the insights tab
    if (activeTab !== "insights") {
      return;
    }

    setIsTransitioning(true);

    // Navigate after animation completes
    setTimeout(() => {
      navigate("/dashboard");
    }, 800);
  };

  return (
    <div ref={containerRef} className="relative min-h-[200vh] bg-crypto-darker overflow-hidden">
      {/* Hero Section with Portal Effect */}
      <motion.div
        className="fixed top-0 left-0 w-full h-screen flex items-center justify-center z-10"
        style={{
          scale: heroScale,
          opacity: heroOpacity,
        }}
      >
        <div className="relative w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Central Pulse */}
          <motion.div
            className="relative flex flex-col items-center justify-center mb-20"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.2 }}
          >
            {/* Main Headline */}
            <h1 className="text-7xl md:text-8xl font-thin text-white text-center leading-tight tracking-tight mb-6 font-sf-pro">
              The Nervous System
              <br />
              <span className="text-gradient font-light">of Crypto</span>
            </h1>

            {/* Subheadline */}
            <p className="text-xl md:text-2xl text-gray-400 text-center max-w-2xl mb-12 font-light">
              Real-time sentiment intelligence. Market volatility detection. One unified signal.
            </p>

            {/* Central Logo with Pulse */}
            <motion.div
              className="relative w-64 h-64 flex items-center justify-center"
              animate={{
                scale: [1, 1.05, 1],
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                ease: "easeInOut",
              }}
            >
              {/* Outer ring */}
              <motion.div
                className="absolute inset-0 rounded-full border-2 border-blue-500/30"
                animate={{
                  scale: [1, 1.2, 1],
                  opacity: [0.3, 0.1, 0.3],
                }}
                transition={{
                  duration: 3,
                  repeat: Infinity,
                  ease: "easeInOut",
                }}
              />

              {/* Middle ring */}
              <motion.div
                className="absolute inset-8 rounded-full border-2 border-green-500/40"
                animate={{
                  scale: [1, 1.15, 1],
                  opacity: [0.4, 0.2, 0.4],
                }}
                transition={{
                  duration: 3,
                  repeat: Infinity,
                  ease: "easeInOut",
                  delay: 0.5,
                }}
              />

              {/* Logo */}
              <motion.img
                src="/icon.png"
                alt="F&G 6900 Logo"
                className="relative w-48 h-48 object-contain drop-shadow-2xl"
                animate={{
                  filter: [
                    "drop-shadow(0 0 20px rgba(59, 130, 246, 0.5))",
                    "drop-shadow(0 0 40px rgba(59, 130, 246, 0.8))",
                    "drop-shadow(0 0 20px rgba(59, 130, 246, 0.5))",
                  ],
                }}
                transition={{
                  duration: 3,
                  repeat: Infinity,
                  ease: "easeInOut",
                }}
              />
            </motion.div>

            {/* CTA Button */}
            <motion.button
              onClick={handleDiveIn}
              className="mt-12 px-8 py-4 glass-card rounded-full text-white font-semibold text-lg hover:bg-blue-500/20 transition-all border-2 border-blue-500/50"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1 }}
            >
              Dive Into The Signal
            </motion.button>
          </motion.div>

          {/* Orbit Cards */}
          {/* Left Orbit: Social Intelligence */}
          <motion.div
            className="absolute left-8 top-1/4 w-80"
            initial={{ opacity: 0, x: -100 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 1, delay: 0.5 }}
          >
            <div className="glass-card rounded-2xl p-6 border-2 border-purple-500/30 hover:border-purple-500/50 transition-all">
              <div className="flex items-center gap-3 mb-4">
                <Twitter className="w-6 h-6 text-purple-400" />
                <h3 className="text-xl font-bold text-white">Social Intelligence</h3>
              </div>
              <p className="text-gray-400 mb-4">Live sentiment from crypto Twitter, Reddit, and Discord.</p>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Sentiment Score</span>
                  <span className="text-lg font-bold text-purple-400">{sentimentScore.toFixed(0)}</span>
                </div>
                <div className="w-full h-2 bg-crypto-darker rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-gradient-to-r from-purple-500 to-pink-500"
                    initial={{ width: "0%" }}
                    animate={{ width: `${sentimentScore}%` }}
                    transition={{ duration: 0.5 }}
                  />
                </div>
              </div>
            </div>
          </motion.div>

          {/* Right Orbit: Market Pulse */}
          <motion.div
            className="absolute right-8 top-1/4 w-80"
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 1, delay: 0.7 }}
          >
            <div className="glass-card rounded-2xl p-6 border-2 border-green-500/30 hover:border-green-500/50 transition-all">
              <div className="flex items-center gap-3 mb-4">
                <TrendingUp className="w-6 h-6 text-green-400" />
                <h3 className="text-xl font-bold text-white">Market Pulse</h3>
              </div>
              <p className="text-gray-400 mb-4">Real-time price action from Binance WebSocket.</p>
              <div className="space-y-3">
                {livePrices.btc && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">BTC</span>
                    <span className="text-lg font-bold text-orange-400">
                      ${livePrices.btc.toLocaleString()}
                    </span>
                  </div>
                )}
                {livePrices.eth && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">ETH</span>
                    <span className="text-lg font-bold text-blue-400">
                      ${livePrices.eth.toLocaleString()}
                    </span>
                  </div>
                )}
                {livePrices.sol && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">SOL</span>
                    <span className="text-lg font-bold text-purple-400">
                      ${livePrices.sol.toLocaleString()}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </motion.div>

          {/* Bottom Orbit: Verified Signal */}
          <motion.div
            className="absolute left-1/2 bottom-12 -translate-x-1/2 w-96"
            initial={{ opacity: 0, y: 100 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.9 }}
          >
            <div className="glass-card rounded-2xl p-6 border-2 border-blue-500/30 hover:border-blue-500/50 transition-all">
              <div className="flex items-center gap-3 mb-4">
                <Shield className="w-6 h-6 text-blue-400" />
                <h3 className="text-xl font-bold text-white">Verified Signal</h3>
              </div>
              <div className="flex items-center gap-4">
                <Zap className="w-8 h-8 text-yellow-400 animate-pulse" />
                <div>
                  <p className="text-sm text-gray-400">Current Index</p>
                  <p className="text-2xl font-bold text-gradient">Fear & Greed 6900</p>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </motion.div>

      {/* Dashboard Preview with Portal Effect */}
      <motion.div
        className="fixed top-0 left-0 w-full h-screen flex items-center justify-center pointer-events-none z-5"
        style={{
          scale: dashboardScale,
          opacity: dashboardOpacity,
          y: dashboardY,
        }}
      >
        <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="glass-card rounded-3xl p-8 border-2 border-blue-500/50 shadow-2xl">
            <div className="flex items-center gap-4 mb-6">
              <Activity className="w-8 h-8 text-blue-400" />
              <h2 className="text-3xl font-bold text-white">Dashboard Loading...</h2>
            </div>
            <div className="space-y-4">
              <div className="h-48 bg-crypto-darker rounded-xl animate-pulse" />
              <div className="grid grid-cols-3 gap-4">
                <div className="h-32 bg-crypto-darker rounded-xl animate-pulse" />
                <div className="h-32 bg-crypto-darker rounded-xl animate-pulse" />
                <div className="h-32 bg-crypto-darker rounded-xl animate-pulse" />
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Agent Gateway Section (Below the fold) */}
      <div className="relative z-20 mt-[100vh] min-h-screen flex items-center justify-center px-4">
        <motion.div
          className="max-w-5xl w-full"
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 1 }}
          viewport={{ once: true }}
        >
          <div className="text-center mb-12">
            <h2 className="text-5xl font-thin text-white mb-4">Agent Gateway</h2>
            <p className="text-2xl text-gray-400 font-light">
              Human Intuition. Machine Speed. One Signal.
            </p>
          </div>

          {/* Terminal Window with Tab Switcher */}
          <motion.div
            className="glass-card rounded-2xl overflow-hidden border-2 border-green-500/30"
            style={{ overflow: "hidden" }}
            animate={
              isTransitioning
                ? {
                    scale: 3,
                    opacity: 0,
                  }
                : { scale: 1, opacity: 1 }
            }
            transition={{ duration: 0.8, ease: "easeInOut" }}
          >
            {/* Terminal Header with Tab Switcher */}
            <div className="relative bg-crypto-darker/80 px-6 py-3 border-b border-green-500/30 z-0">
              <div className="flex items-center gap-4 mb-3">
                <div className="flex gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-500" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500" />
                  <div className="w-3 h-3 rounded-full bg-green-500" />
                </div>
                <Terminal className="w-4 h-4 text-green-400" />
                <span className="text-sm text-gray-400 font-mono">Moltbot & OpenClaw Terminal</span>
              </div>

              {/* Tab Switcher */}
              <div className="relative flex gap-1 p-1 bg-crypto-darker/60 rounded-lg isolate">
                {/* Animated pill background */}
                <motion.div
                  className="absolute h-[calc(100%-8px)] bg-green-500/20 rounded-md border border-green-500/40"
                  style={{ zIndex: 10 }}
                  layoutId="activeTabPill"
                  initial={false}
                  animate={{
                    x: activeTab === "signal" ? 4 : "calc(50% + 2px)",
                    width: activeTab === "signal" ? "calc(50% - 6px)" : "calc(50% - 6px)",
                  }}
                  transition={{
                    type: "spring",
                    stiffness: 500,
                    damping: 35,
                  }}
                />

                {/* Tab buttons */}
                <button
                  onClick={() => setActiveTab("signal")}
                  className={`relative z-20 flex-1 px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                    activeTab === "signal" ? "text-green-400" : "text-gray-400 hover:text-gray-300"
                  }`}
                >
                  Agent Signal (JSON)
                </button>
                <button
                  onClick={() => setActiveTab("insights")}
                  className={`relative z-20 flex-1 px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                    activeTab === "insights" ? "text-green-400" : "text-gray-400 hover:text-gray-300"
                  }`}
                >
                  Index Insights
                </button>
              </div>
            </div>

            {/* Tab Content - Fixed Height Container */}
            <motion.div className="relative h-[400px] overflow-hidden">
              <AnimatePresence mode="wait" initial={false}>
                {activeTab === "signal" ? (
                  /* JSON Code Block */
                  <motion.div
                    key="signal"
                    variants={tabContentVariants}
                    initial="enter"
                    animate="center"
                    exit="exit"
                    className="absolute inset-0 p-6 font-mono text-sm"
                  >
                    <pre className="text-gray-300">
                      <code>
                        <span className="text-purple-400">POST</span>{" "}
                        <span className="text-green-400">/api/v1/agent/signal</span>
                        {"\n\n"}
                        <span className="text-gray-500">// Request</span>
                        {"\n"}
                        <span className="text-blue-400">{"{"}</span>
                        {"\n"}
                        {"  "}
                        <span className="text-orange-400">"agent_id"</span>:{" "}
                        <span className="text-green-300">"moltbot_v1"</span>,{"\n"}
                        {"  "}
                        <span className="text-orange-400">"query"</span>:{" "}
                        <span className="text-green-300">"analyze current market sentiment"</span>
                        {"\n"}
                        <span className="text-blue-400">{"}"}</span>
                        {"\n\n"}
                        <span className="text-gray-500">// Response (Live)</span>
                        {"\n"}
                        <span className="text-blue-400">{"{"}</span>
                        {"\n"}
                        {"  "}
                        <span className="text-orange-400">"index_score"</span>:{" "}
                        <span className="text-yellow-300">
                          {agentSignal?.index_score || 32}
                        </span>
                        ,{"\n"}
                        {"  "}
                        <span className="text-orange-400">"sentiment"</span>:{" "}
                        <span className="text-green-300">
                          "{agentSignal?.sentiment || "FEAR"}"
                        </span>
                        ,{"\n"}
                        {"  "}
                        <span className="text-orange-400">"recommendation"</span>:{" "}
                        <span className="text-green-300">
                          "{agentSignal?.recommendation || "ACCUMULATE_BTC"}"
                        </span>
                        ,{"\n"}
                        {"  "}
                        <span className="text-orange-400">"is_volatile"</span>:{" "}
                        <span className="text-yellow-300">
                          {agentSignal?.is_volatile ? "true" : "false"}
                        </span>
                        ,{"\n"}
                        {"  "}
                        <span className="text-orange-400">"timestamp"</span>:{" "}
                        <span className="text-green-300">
                          "{agentSignal?.timestamp || new Date().toISOString()}"
                        </span>
                        {"\n"}
                        <span className="text-blue-400">{"}"}</span>
                      </code>
                    </pre>
                  </motion.div>
                ) : (
                  /* Dashboard Preview */
                  <motion.div
                    key="insights"
                    variants={tabContentVariants}
                    initial="enter"
                    animate="center"
                    exit="exit"
                    className="absolute inset-0 p-6 flex flex-col items-center justify-center space-y-8"
                  >
                    {/* Minimized Gauge */}
                    <div className="relative">
                      <motion.div
                        className="relative w-48 h-24"
                        initial={{ scale: 0.8, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        transition={{ delay: 0.1 }}
                      >
                        {/* Mini gauge SVG */}
                        <svg className="w-full h-full" viewBox="0 0 200 100">
                          <defs>
                            <linearGradient id="miniGaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                              <stop offset="0%" stopColor="#ef4444" />
                              <stop offset="25%" stopColor="#f97316" />
                              <stop offset="50%" stopColor="#f59e0b" />
                              <stop offset="75%" stopColor="#84cc16" />
                              <stop offset="100%" stopColor="#10b981" />
                            </linearGradient>
                          </defs>

                          {/* Background arc */}
                          <path
                            d="M 20 90 A 80 80 0 0 1 180 90"
                            fill="none"
                            stroke="url(#miniGaugeGradient)"
                            strokeWidth="16"
                            strokeLinecap="round"
                            opacity="0.3"
                          />

                          {/* Active arc */}
                          <motion.path
                            d="M 20 90 A 80 80 0 0 1 180 90"
                            fill="none"
                            stroke="url(#miniGaugeGradient)"
                            strokeWidth="16"
                            strokeLinecap="round"
                            strokeDasharray={`${((agentSignal?.index_score || 32) / 100) * 251.2} 251.2`}
                            initial={{ strokeDasharray: "0 251.2" }}
                            animate={{
                              strokeDasharray: `${((agentSignal?.index_score || 32) / 100) * 251.2} 251.2`,
                            }}
                            transition={{ duration: 1.5, ease: "easeOut" }}
                          />
                        </svg>

                        {/* Score display */}
                        <motion.div
                          className="absolute bottom-0 left-1/2 -translate-x-1/2 text-center"
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: 0.2 }}
                        >
                          <p className="text-4xl font-bold text-gradient">
                            {agentSignal?.index_score || 32}
                          </p>
                          <p className="text-sm text-green-400 font-semibold uppercase">
                            {agentSignal?.sentiment || "FEAR"}
                          </p>
                        </motion.div>
                      </motion.div>
                    </div>

                    {/* Stats Row */}
                    <motion.div
                      className="grid grid-cols-2 gap-4 w-full max-w-md"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.15 }}
                    >
                      <div className="glass-card rounded-lg p-4 text-center">
                        <p className="text-xs text-gray-500 mb-1">Recommendation</p>
                        <p className="text-sm font-bold text-green-400">
                          {agentSignal?.recommendation || "ACCUMULATE_BTC"}
                        </p>
                      </div>
                      <div className="glass-card rounded-lg p-4 text-center">
                        <p className="text-xs text-gray-500 mb-1">Volatility</p>
                        <p className="text-2xl font-bold text-yellow-400">
                          {agentSignal?.is_volatile ? "HIGH" : "LOW"}
                        </p>
                      </div>
                    </motion.div>

                    {/* Launch Button */}
                    <motion.button
                      onClick={handleLaunchDashboard}
                      className="px-8 py-4 bg-gradient-to-r from-green-500 to-blue-500 rounded-full text-white font-bold text-lg shadow-2xl hover:shadow-green-500/50 transition-all"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.25 }}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      Launch Full Dashboard →
                    </motion.button>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          </motion.div>

          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
            <motion.div
              className="glass-card rounded-xl p-6 text-center"
              whileHover={{ scale: 1.05 }}
            >
              <Activity className="w-12 h-12 text-blue-400 mx-auto mb-4" />
              <h3 className="text-xl font-bold text-white mb-2">Real-Time Analysis</h3>
              <p className="text-gray-400">Sub-second latency on market signals</p>
            </motion.div>

            <motion.div
              className="glass-card rounded-xl p-6 text-center"
              whileHover={{ scale: 1.05 }}
            >
              <Shield className="w-12 h-12 text-green-400 mx-auto mb-4" />
              <h3 className="text-xl font-bold text-white mb-2">Verified Sources</h3>
              <p className="text-gray-400">CoinMarketCap + Binance data streams</p>
            </motion.div>

            <motion.div
              className="glass-card rounded-xl p-6 text-center"
              whileHover={{ scale: 1.05 }}
            >
              <Zap className="w-12 h-12 text-yellow-400 mx-auto mb-4" />
              <h3 className="text-xl font-bold text-white mb-2">AI-Powered</h3>
              <p className="text-gray-400">Machine learning sentiment detection</p>
            </motion.div>
          </div>
        </motion.div>
      </div>

      {/* Scroll Indicator */}
      <motion.div
        className="fixed bottom-8 left-1/2 -translate-x-1/2 z-30"
        initial={{ opacity: 1 }}
        animate={{ opacity: scrollYProgress.get() > 0.1 ? 0 : 1 }}
      >
        <motion.div
          className="flex flex-col items-center gap-2 text-gray-400"
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <span className="text-sm font-light">Scroll to dive in</span>
          <div className="w-6 h-10 rounded-full border-2 border-gray-400 flex items-start justify-center pt-2">
            <motion.div
              className="w-1 h-2 bg-gray-400 rounded-full"
              animate={{ y: [0, 12, 0] }}
              transition={{ duration: 2, repeat: Infinity }}
            />
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
}
