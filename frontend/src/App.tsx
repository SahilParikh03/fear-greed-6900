import { useEffect, useState, useCallback } from "react";
import { RefreshCw, Activity, AlertCircle, CheckCircle2, Zap } from "lucide-react";
import { AnimatedGauge } from "./components/AnimatedGauge";
import { HistoryChart } from "./components/HistoryChart";
import { ScoreCard } from "./components/ScoreCard";
import { SignalIsland } from "./components/SignalIsland";
import { OdometerNumber } from "./components/OdometerNumber";
import { apiClient } from "./utils/api";
import type { IndexData, HistoryData } from "./types";
import { cn } from "./utils/cn";
import { motion } from "framer-motion";
import { playAlertSound, unlockAudioContext } from "./utils/sound";

interface VolatilityEvent {
  type: "volatility_spike";
  asset?: string;
  current_price: number;
  price_change: number;
  change_percent: number;
  window_minutes: number;
  timestamp: string;
  volatility_alert: boolean;
}

interface CrashEvent {
  asset: "BTC" | "ETH" | "SOL";
  type: "VOLATILITY_CRASH";
  magnitude: number;
  current_price: number;
  peak_price: number;
  price_drop: number;
  timestamp: string;
  buffer_size: number;
}

interface PriceEvent {
  type: "price_update";
  asset: string;
  symbol: string;
  price: number;
  quantity: number;
  timestamp: string;
}

function App() {
  const [indexData, setIndexData] = useState<IndexData | null>(null);
  const [historyData, setHistoryData] = useState<HistoryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  // Real-time data
  const [btcPrice, setBtcPrice] = useState<number | null>(null);
  const [ethPrice, setEthPrice] = useState<number | null>(null);
  const [solPrice, setSolPrice] = useState<number | null>(null);
  const [volatilityEvent, setVolatilityEvent] = useState<VolatilityEvent | null>(null);
  const [crashEvent, setCrashEvent] = useState<CrashEvent | null>(null);
  const [isVolatile, setIsVolatile] = useState(false);

  // Unlock audio context on first user interaction
  useEffect(() => {
    const handleFirstInteraction = () => {
      unlockAudioContext();
      window.removeEventListener("click", handleFirstInteraction);
      window.removeEventListener("keydown", handleFirstInteraction);
    };

    window.addEventListener("click", handleFirstInteraction);
    window.addEventListener("keydown", handleFirstInteraction);

    return () => {
      window.removeEventListener("click", handleFirstInteraction);
      window.removeEventListener("keydown", handleFirstInteraction);
    };
  }, []);

  const fetchData = async () => {
    try {
      setError(null);
      const [index, history] = await Promise.all([
        apiClient.getIndex(),
        apiClient.getHistory(7),
      ]);
      setIndexData(index);
      setHistoryData(history);
      setLastUpdate(new Date());
    } catch (err: any) {
      console.error("Failed to fetch data:", err);
      setError(
        err.response?.data?.detail ||
          err.message ||
          "Failed to fetch data. Make sure the backend is running on http://localhost:8000"
      );
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    setError(null);
    try {
      // Trigger backend refresh
      await apiClient.refreshData();

      // Wait 2 seconds for backend to process
      setTimeout(async () => {
        await fetchData();
        setRefreshing(false);
      }, 2000);
    } catch (err: any) {
      console.error("Failed to refresh:", err);
      setError(err.response?.data?.detail || err.message || "Failed to refresh data");
      setRefreshing(false);
    }
  };

  // Connect to SSE for real-time updates
  useEffect(() => {
    const connectSSE = () => {
      const eventSource = new EventSource("http://localhost:8000/api/v1/stream");

      eventSource.onopen = () => {
        console.log("Connected to Apple-Sleek Stream");
      };

      eventSource.addEventListener("price", (event) => {
        try {
          const priceData: PriceEvent = JSON.parse(event.data);
          // Update asset-specific price state
          switch (priceData.asset) {
            case "BTC":
              setBtcPrice(priceData.price);
              break;
            case "ETH":
              setEthPrice(priceData.price);
              break;
            case "SOL":
              setSolPrice(priceData.price);
              break;
          }
        } catch (err) {
          console.error("Failed to parse price event:", err);
        }
      });

      eventSource.addEventListener("volatility", (event) => {
        try {
          const volatilityData: VolatilityEvent = JSON.parse(event.data);
          setVolatilityEvent(volatilityData);
          setIsVolatile(true);

          // Clear volatile state after 30 seconds
          setTimeout(() => {
            setIsVolatile(false);
          }, 30000);
        } catch (err) {
          console.error("Failed to parse volatility event:", err);
        }
      });

      eventSource.addEventListener("crash", (event) => {
        try {
          const crashData: CrashEvent = JSON.parse(event.data);
          console.log("🚨 VOLATILITY_CRASH received:", crashData);

          // Play asset-specific alert sound
          playAlertSound(crashData.asset);

          // Set crash event for visual alert
          setCrashEvent(crashData);
          setIsVolatile(true);

          // Clear crash event after 30 seconds
          setTimeout(() => {
            setCrashEvent(null);
            setIsVolatile(false);
          }, 30000);
        } catch (err) {
          console.error("Failed to parse crash event:", err);
        }
      });

      eventSource.onerror = () => {
        console.error("SSE connection error. Reconnecting...");
        eventSource.close();
        setTimeout(connectSSE, 5000);
      };

      return eventSource;
    };

    const eventSource = connectSSE();

    return () => {
      eventSource.close();
    };
  }, []);

  useEffect(() => {
    fetchData();
    // Auto-refresh every 5 minutes
    const interval = setInterval(fetchData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const handleDismissVolatility = useCallback(() => {
    setVolatilityEvent(null);
    setCrashEvent(null);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-crypto-darker flex items-center justify-center">
        <motion.div
          className="text-center"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          <Activity className="w-12 h-12 text-blue-500 animate-pulse mx-auto mb-4" />
          <p className="text-gray-400 text-lg font-sf-pro">Loading Fear & Greed Index...</p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-crypto-darker">
      {/* Signal Island for Volatility Alerts - prioritize crash events over volatility */}
      <SignalIsland event={crashEvent || volatilityEvent} onDismiss={handleDismissVolatility} />

      {/* Header */}
      <motion.header
        className="glass-card border-b border-crypto-border/50 sticky top-0 z-40 backdrop-blur-glass"
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ type: "spring", stiffness: 100 }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gradient font-sf-pro">
                Fear & Greed Index 6900
              </h1>
              <p className="text-gray-400 mt-1 font-medium">
                Custom Crypto Market Sentiment Analysis
              </p>
            </div>

            <div className="flex items-center gap-4">
              {/* Live BTC Price */}
              {btcPrice && (
                <motion.div
                  className="glass-card px-4 py-2 rounded-lg flex items-center gap-2"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  whileHover={{ scale: 1.05 }}
                >
                  <Zap className="w-4 h-4 text-orange-500" />
                  <div className="text-right">
                    <p className="text-xs text-gray-500 font-medium">₿ BTC</p>
                    <OdometerNumber
                      value={btcPrice}
                      decimals={2}
                      prefix="$"
                      className="text-sm font-bold text-white"
                    />
                  </div>
                </motion.div>
              )}

              {/* Live ETH Price */}
              {ethPrice && (
                <motion.div
                  className="glass-card px-4 py-2 rounded-lg flex items-center gap-2"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.1 }}
                  whileHover={{ scale: 1.05 }}
                >
                  <Zap className="w-4 h-4 text-blue-500" />
                  <div className="text-right">
                    <p className="text-xs text-gray-500 font-medium">Ξ ETH</p>
                    <OdometerNumber
                      value={ethPrice}
                      decimals={2}
                      prefix="$"
                      className="text-sm font-bold text-white"
                    />
                  </div>
                </motion.div>
              )}

              {/* Live SOL Price */}
              {solPrice && (
                <motion.div
                  className="glass-card px-4 py-2 rounded-lg flex items-center gap-2"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2 }}
                  whileHover={{ scale: 1.05 }}
                >
                  <Zap className="w-4 h-4 text-purple-500" />
                  <div className="text-right">
                    <p className="text-xs text-gray-500 font-medium">◎ SOL</p>
                    <OdometerNumber
                      value={solPrice}
                      decimals={2}
                      prefix="$"
                      className="text-sm font-bold text-white"
                    />
                  </div>
                </motion.div>
              )}

              <motion.button
                onClick={handleRefresh}
                disabled={refreshing}
                className={cn(
                  "flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all glass-card",
                  "bg-blue-500/20 hover:bg-blue-500/30 text-white border border-blue-500/30",
                  "disabled:opacity-50 disabled:cursor-not-allowed",
                  refreshing && "animate-pulse"
                )}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <RefreshCw className={cn("w-4 h-4", refreshing && "animate-spin")} />
                {refreshing ? "Refreshing..." : "Refresh"}
              </motion.button>
            </div>
          </div>
        </div>
      </motion.header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Alert */}
        {error && (
          <div className="mb-6 bg-fear-red/10 border border-fear-red/30 rounded-lg p-4 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-fear-red flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-fear-red font-semibold mb-1">Error</h3>
              <p className="text-gray-300 text-sm">{error}</p>
            </div>
          </div>
        )}

        {/* Last Update */}
        {lastUpdate && (
          <div className="mb-6 flex items-center gap-2 text-sm text-gray-500">
            <CheckCircle2 className="w-4 h-4 text-greed-green" />
            Last updated: {lastUpdate.toLocaleTimeString()}
          </div>
        )}

        {indexData && historyData ? (
          <div className="space-y-6">
            {/* Top Section: Gauge + Chart */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <AnimatedGauge
                score={indexData.master_score}
                sentiment={indexData.sentiment}
                isVolatile={isVolatile}
              />
              <HistoryChart data={historyData.data} />
            </div>

            {/* Component Breakdown */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <h2 className="text-2xl font-bold text-white mb-4 font-sf-pro">
                Component Breakdown
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <ScoreCard
                  title="Volatility"
                  score={indexData.component_details.volatility}
                  weight={indexData.weights.volatility}
                  icon="volatility"
                />
                <ScoreCard
                  title="BTC Dominance"
                  score={indexData.component_details.dominance}
                  weight={indexData.weights.dominance}
                  icon="dominance"
                />
                <ScoreCard
                  title="Social Sentiment"
                  score={indexData.component_details.social}
                  weight={indexData.weights.social}
                  icon="social"
                />
              </div>
            </motion.div>

            {/* Footer Stats */}
            <motion.div
              className="glass-card rounded-xl p-6 mt-8"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                <motion.div whileHover={{ scale: 1.05 }}>
                  <p className="text-gray-500 text-sm mb-1 font-medium">Master Score</p>
                  <OdometerNumber
                    value={indexData.master_score}
                    decimals={0}
                    className="text-2xl font-bold text-white"
                  />
                </motion.div>
                <motion.div whileHover={{ scale: 1.05 }}>
                  <p className="text-gray-500 text-sm mb-1 font-medium">Volatility</p>
                  <OdometerNumber
                    value={indexData.breakdown.volatility}
                    decimals={0}
                    className="text-2xl font-bold text-white"
                  />
                </motion.div>
                <motion.div whileHover={{ scale: 1.05 }}>
                  <p className="text-gray-500 text-sm mb-1 font-medium">Dominance</p>
                  <OdometerNumber
                    value={indexData.breakdown.dominance}
                    decimals={0}
                    className="text-2xl font-bold text-white"
                  />
                </motion.div>
                <motion.div whileHover={{ scale: 1.05 }}>
                  <p className="text-gray-500 text-sm mb-1 font-medium">Social</p>
                  <OdometerNumber
                    value={indexData.breakdown.social}
                    decimals={0}
                    className="text-2xl font-bold text-white"
                  />
                </motion.div>
              </div>
            </motion.div>
          </div>
        ) : (
          <div className="text-center py-12">
            <AlertCircle className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400 text-lg">No data available</p>
            <button
              onClick={fetchData}
              className="mt-4 px-6 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg"
            >
              Try Again
            </button>
          </div>
        )}
      </main>

      {/* Footer */}
      <motion.footer
        className="glass-card border-t border-crypto-border/50 mt-12"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-gray-500 text-sm font-medium">
            Fear & Greed Index 6900 • Custom Crypto Sentiment Analysis • Real-time by Binance • Powered by CoinMarketCap
          </p>
        </div>
      </motion.footer>
    </div>
  );
}

export default App;
