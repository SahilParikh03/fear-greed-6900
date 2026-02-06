import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, Activity, Users, Zap } from "lucide-react";
import { cn } from "../utils/cn";
import { OdometerNumber } from "./OdometerNumber";
import type { ComponentScore } from "../types";

interface ScoreCardProps {
  title: string;
  score: ComponentScore;
  weight: number;
  icon: "volatility" | "dominance" | "social";
}

export function ScoreCard({ title, score, weight, icon }: ScoreCardProps) {
  const getIcon = () => {
    switch (icon) {
      case "volatility":
        return <Activity className="w-6 h-6" />;
      case "dominance":
        return <Zap className="w-6 h-6" />;
      case "social":
        return <Users className="w-6 h-6" />;
    }
  };

  const getSignalColor = (signal: string) => {
    if (signal.includes("Fear") || signal.includes("Bearish")) return "text-fear-red";
    if (signal.includes("Greed") || signal.includes("Bullish")) return "text-greed-green";
    return "text-neutral-yellow";
  };

  const getSignalBg = (signal: string) => {
    if (signal.includes("Fear") || signal.includes("Bearish"))
      return "bg-fear-red/10 border-fear-red/30";
    if (signal.includes("Greed") || signal.includes("Bullish"))
      return "bg-greed-green/10 border-greed-green/30";
    return "bg-neutral-yellow/10 border-neutral-yellow/30";
  };

  const getSignalIcon = (signal: string) => {
    if (signal.includes("Fear") || signal.includes("Bearish")) {
      return <TrendingDown className="w-4 h-4" />;
    }
    if (signal.includes("Greed") || signal.includes("Bullish")) {
      return <TrendingUp className="w-4 h-4" />;
    }
    return <Activity className="w-4 h-4" />;
  };

  // Calculate progress bar width
  const progressWidth = score.score;

  return (
    <motion.div
      className="glass-card glass-card-hover rounded-xl p-5"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      whileHover={{ scale: 1.02 }}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <motion.div
            className="p-2 bg-blue-500/10 rounded-lg text-blue-400"
            whileHover={{ scale: 1.1, rotate: 5 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            {getIcon()}
          </motion.div>
          <div>
            <h3 className="text-lg font-semibold text-white font-sf-pro">{title}</h3>
            <p className="text-xs text-gray-500 font-medium">
              Weight: {(weight * 100).toFixed(0)}%
            </p>
          </div>
        </div>
        <div className="text-right">
          <OdometerNumber
            value={score.score}
            decimals={0}
            className="text-2xl font-bold text-white"
          />
          <p className="text-xs text-gray-500 font-medium">Score</p>
        </div>
      </div>

      {/* Progress bar */}
      <div className="mb-4">
        <div className="h-2 bg-crypto-darker/50 rounded-full overflow-hidden backdrop-blur-sm">
          <motion.div
            className={cn(
              "h-full rounded-full",
              score.score < 30 ? "bg-fear-red" : "",
              score.score >= 30 && score.score < 45 ? "bg-orange-500" : "",
              score.score >= 45 && score.score < 55 ? "bg-neutral-yellow" : "",
              score.score >= 55 && score.score < 70 ? "bg-lime-500" : "",
              score.score >= 70 ? "bg-greed-green" : ""
            )}
            initial={{ width: 0 }}
            animate={{ width: `${progressWidth}%` }}
            transition={{ duration: 1, ease: "easeOut" }}
          />
        </div>
      </div>

      {/* Signal badge */}
      <motion.div
        className={cn(
          "inline-flex items-center gap-2 px-3 py-1.5 rounded-lg border mb-3",
          getSignalBg(score.signal)
        )}
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        <motion.span
          className={getSignalColor(score.signal)}
          animate={{ rotate: [0, 5, -5, 0] }}
          transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
        >
          {getSignalIcon(score.signal)}
        </motion.span>
        <span className={cn("text-sm font-medium", getSignalColor(score.signal))}>
          {score.signal}
        </span>
      </motion.div>

      {/* Reasoning */}
      <motion.p
        className="text-sm text-gray-400 leading-relaxed"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        {score.reasoning}
      </motion.p>
    </motion.div>
  );
}
