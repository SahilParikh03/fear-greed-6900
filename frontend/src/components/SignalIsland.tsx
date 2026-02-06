import { motion, AnimatePresence } from "framer-motion";
import { TrendingUp, TrendingDown, X, AlertTriangle } from "lucide-react";
import { useState, useEffect } from "react";
import { cn } from "../utils/cn";

interface VolatilityEvent {
  type: "volatility_spike";
  asset?: string;
  current_price: number;
  price_change: number;
  change_percent: number;
  window_minutes: number;
  timestamp: string;
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

interface SignalIslandProps {
  event: VolatilityEvent | CrashEvent | null;
  onDismiss: () => void;
}

export function SignalIsland({ event, onDismiss }: SignalIslandProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    if (event) {
      setIsExpanded(true);

      // Auto-collapse after 5 seconds
      const collapseTimer = setTimeout(() => {
        setIsExpanded(false);
      }, 5000);

      // Auto-dismiss after 10 seconds
      const dismissTimer = setTimeout(() => {
        onDismiss();
      }, 10000);

      return () => {
        clearTimeout(collapseTimer);
        clearTimeout(dismissTimer);
      };
    }
  }, [event, onDismiss]);

  if (!event) return null;

  // Determine event type
  const isCrashEvent = event.type === "VOLATILITY_CRASH";
  const isVolatilityEvent = event.type === "volatility_spike";

  // For crash events, always negative (price drop)
  // For volatility events, check price_change direction
  const isPositive = isCrashEvent ? false : (event as VolatilityEvent).price_change > 0;

  // Get asset-specific colors
  const assetColors = {
    BTC: { glow: "glow-orange", bg: "bg-orange-500/20", text: "text-orange-500", emoji: "₿" },
    ETH: { glow: "glow-blue", bg: "bg-blue-500/20", text: "text-blue-500", emoji: "Ξ" },
    SOL: { glow: "glow-purple", bg: "bg-purple-500/20", text: "text-purple-500", emoji: "◎" },
  };

  const asset = event.asset || "BTC";
  const assetStyle = assetColors[asset as keyof typeof assetColors] || assetColors.BTC;

  return (
    <AnimatePresence>
      {event && (
        <motion.div
          className="fixed top-4 left-1/2 z-50"
          initial={{ x: "-50%", y: -100, opacity: 0 }}
          animate={{ x: "-50%", y: 0, opacity: 1 }}
          exit={{ y: -100, opacity: 0 }}
          transition={{ type: "spring", stiffness: 300, damping: 30 }}
        >
          <motion.div
            className={cn(
              "glass-card overflow-hidden cursor-pointer",
              "shadow-2xl",
              isCrashEvent ? assetStyle.glow : (isPositive ? "glow-green" : "glow-red")
            )}
            animate={{
              width: isExpanded ? "400px" : "200px",
              height: isExpanded ? "auto" : "44px",
              borderRadius: isExpanded ? "20px" : "22px",
            }}
            transition={{ duration: 0.4, ease: "easeInOut" }}
            onClick={() => setIsExpanded(!isExpanded)}
          >
            {/* Compact View */}
            <motion.div
              className="flex items-center justify-between px-4 py-2"
              initial={false}
              animate={{ opacity: isExpanded ? 0 : 1 }}
              transition={{ duration: 0.2 }}
            >
              <div className="flex items-center gap-2">
                <motion.div
                  className={cn(
                    "w-2 h-2 rounded-full",
                    isCrashEvent ? assetStyle.text.replace("text-", "bg-") : (isPositive ? "bg-greed-green" : "bg-fear-red")
                  )}
                  animate={{ scale: [1, 1.5, 1] }}
                  transition={{ duration: 1, repeat: Infinity }}
                />
                <span className="text-white text-sm font-semibold">
                  {isCrashEvent ? `${assetStyle.emoji} ${asset} Quick Drop` : "🚨 Volatility Alert"}
                </span>
              </div>
            </motion.div>

            {/* Expanded View */}
            <AnimatePresence>
              {isExpanded && (
                <motion.div
                  className="p-4"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.3, delay: 0.1 }}
                >
                  {/* Header */}
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <motion.div
                        className={cn(
                          "p-2 rounded-full",
                          isCrashEvent
                            ? `${assetStyle.bg} ${assetStyle.text}`
                            : (isPositive
                              ? "bg-greed-green/20 text-greed-green"
                              : "bg-fear-red/20 text-fear-red")
                        )}
                        animate={{ rotate: [0, 360] }}
                        transition={{ duration: 2, ease: "linear" }}
                      >
                        {isCrashEvent ? (
                          <AlertTriangle className="w-5 h-5" />
                        ) : isPositive ? (
                          <TrendingUp className="w-5 h-5" />
                        ) : (
                          <TrendingDown className="w-5 h-5" />
                        )}
                      </motion.div>
                      <div>
                        <h3 className="text-white font-bold text-lg font-sf-pro">
                          {isCrashEvent ? `${asset} Quick Drop` : "Volatility Spike"}
                        </h3>
                        <p className="text-gray-400 text-xs">
                          {isCrashEvent
                            ? `~5 min buffer (${(event as CrashEvent).buffer_size} points)`
                            : `${(event as VolatilityEvent).window_minutes} minute window`
                          }
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onDismiss();
                      }}
                      className="text-gray-400 hover:text-white transition-colors"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>

                  {/* Stats */}
                  <div className="space-y-2 mb-3">
                    {isCrashEvent ? (
                      // Crash event stats
                      <>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-400 text-sm">Drop Magnitude</span>
                          <span className={cn("text-lg font-bold tabular-nums", assetStyle.text)}>
                            -{(event as CrashEvent).magnitude.toFixed(2)}%
                          </span>
                        </div>

                        <div className="flex justify-between items-center">
                          <span className="text-gray-400 text-sm">Price Drop</span>
                          <span className={cn("text-lg font-bold tabular-nums", assetStyle.text)}>
                            -${(event as CrashEvent).price_drop.toFixed(2)}
                          </span>
                        </div>

                        <div className="flex justify-between items-center">
                          <span className="text-gray-400 text-sm">Peak Price</span>
                          <span className="text-gray-300 font-bold tabular-nums">
                            ${(event as CrashEvent).peak_price.toLocaleString()}
                          </span>
                        </div>

                        <div className="flex justify-between items-center">
                          <span className="text-gray-400 text-sm">Current {asset}</span>
                          <span className="text-white font-bold tabular-nums">
                            ${event.current_price.toLocaleString()}
                          </span>
                        </div>
                      </>
                    ) : (
                      // Volatility event stats
                      <>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-400 text-sm">Price Movement</span>
                          <span
                            className={cn(
                              "text-lg font-bold tabular-nums",
                              isPositive ? "text-greed-green" : "text-fear-red"
                            )}
                          >
                            {isPositive ? "+" : ""}${(event as VolatilityEvent).price_change.toFixed(2)}
                          </span>
                        </div>

                        <div className="flex justify-between items-center">
                          <span className="text-gray-400 text-sm">Percentage</span>
                          <span
                            className={cn(
                              "text-lg font-bold tabular-nums",
                              isPositive ? "text-greed-green" : "text-fear-red"
                            )}
                          >
                            {isPositive ? "+" : ""}
                            {(event as VolatilityEvent).change_percent.toFixed(2)}%
                          </span>
                        </div>

                        <div className="flex justify-between items-center">
                          <span className="text-gray-400 text-sm">Current {asset}</span>
                          <span className="text-white font-bold tabular-nums">
                            ${event.current_price.toLocaleString()}
                          </span>
                        </div>
                      </>
                    )}
                  </div>

                  {/* Progress bar */}
                  <motion.div
                    className={cn(
                      "h-1 rounded-full",
                      isCrashEvent
                        ? assetStyle.bg
                        : (isPositive ? "bg-greed-green/30" : "bg-fear-red/30")
                    )}
                  >
                    <motion.div
                      className={cn(
                        "h-full rounded-full",
                        isCrashEvent
                          ? assetStyle.text.replace("text-", "bg-")
                          : (isPositive ? "bg-greed-green" : "bg-fear-red")
                      )}
                      initial={{ width: "0%" }}
                      animate={{ width: "100%" }}
                      transition={{ duration: 10 }}
                    />
                  </motion.div>

                  <p className="text-xs text-gray-500 text-center mt-2">
                    Tap to {isExpanded ? "collapse" : "expand"}
                  </p>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
