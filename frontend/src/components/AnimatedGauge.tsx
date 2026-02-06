import { motion, useSpring } from "framer-motion";
import { useEffect, useState } from "react";
import { cn } from "../utils/cn";
import { OdometerNumber } from "./OdometerNumber";

interface AnimatedGaugeProps {
  score: number;
  sentiment: string;
  isVolatile?: boolean;
}

export function AnimatedGauge({ score, sentiment, isVolatile = false }: AnimatedGaugeProps) {
  const [displayScore, setDisplayScore] = useState(score);

  // Spring animation for needle rotation
  const rotation = useSpring(-90, {
    damping: 20,
    stiffness: 80,
  });

  useEffect(() => {
    setDisplayScore(score);
    const targetRotation = (score / 100) * 180 - 90;
    rotation.set(targetRotation);
  }, [score, rotation]);

  // Calculate color based on score (0-100)
  const getColor = (score: number) => {
    if (score < 30) return "text-fear-red";
    if (score < 45) return "text-orange-500";
    if (score < 55) return "text-neutral-yellow";
    if (score < 70) return "text-lime-500";
    return "text-greed-green";
  };

  const getGlowColor = (score: number) => {
    if (score < 30) return "glow-red";
    if (score < 45) return "shadow-orange-500/30";
    if (score < 55) return "shadow-yellow-500/30";
    if (score < 70) return "shadow-lime-500/30";
    return "glow-green";
  };

  const getBackgroundColor = (score: number) => {
    if (score < 30) return "from-fear-red/20 to-fear-red/5";
    if (score < 45) return "from-orange-500/20 to-orange-500/5";
    if (score < 55) return "from-neutral-yellow/20 to-neutral-yellow/5";
    if (score < 70) return "from-lime-500/20 to-lime-500/5";
    return "from-greed-green/20 to-greed-green/5";
  };

  const getSentimentEmoji = (score: number) => {
    if (score < 30) return "😱";
    if (score < 45) return "😰";
    if (score < 55) return "😐";
    if (score < 70) return "😊";
    return "🤑";
  };

  return (
    <motion.div
      className={cn(
        "relative overflow-hidden rounded-2xl glass-card p-8",
        "bg-gradient-to-br",
        getBackgroundColor(displayScore)
      )}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
    >
      {/* Header */}
      <motion.div
        className="text-center mb-8"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <h2 className="text-2xl font-bold text-white mb-2 font-sf-pro">
          Fear & Greed Index
        </h2>
        <p className="text-gray-400 text-sm font-medium">Live Crypto Market Sentiment</p>
      </motion.div>

      {/* Gauge Container */}
      <div className="relative flex flex-col items-center">
        {/* Semi-circle gauge background */}
        <div className="relative w-64 h-32 mb-4">
          {/* Gradient arc background */}
          <svg className="w-full h-full" viewBox="0 0 200 100">
            <defs>
              <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#ef4444" />
                <stop offset="25%" stopColor="#f97316" />
                <stop offset="50%" stopColor="#f59e0b" />
                <stop offset="75%" stopColor="#84cc16" />
                <stop offset="100%" stopColor="#10b981" />
              </linearGradient>

              {/* Glow filter for volatile state */}
              <filter id="glow">
                <feGaussianBlur stdDeviation="4" result="coloredBlur" />
                <feMerge>
                  <feMergeNode in="coloredBlur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>

            {/* Background arc */}
            <motion.path
              d="M 20 90 A 80 80 0 0 1 180 90"
              fill="none"
              stroke="url(#gaugeGradient)"
              strokeWidth="20"
              strokeLinecap="round"
              opacity="0.3"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 1.5, ease: "easeOut" }}
            />

            {/* Active arc */}
            <motion.path
              d="M 20 90 A 80 80 0 0 1 180 90"
              fill="none"
              stroke="url(#gaugeGradient)"
              strokeWidth="20"
              strokeLinecap="round"
              strokeDasharray={`${(displayScore / 100) * 251.2} 251.2`}
              filter={isVolatile ? "url(#glow)" : undefined}
              className={isVolatile ? "animate-pulse-slow" : ""}
              initial={{ strokeDasharray: "0 251.2" }}
              animate={{ strokeDasharray: `${(displayScore / 100) * 251.2} 251.2` }}
              transition={{ duration: 1.5, ease: "easeOut", delay: 0.3 }}
            />
          </svg>

          {/* Animated Needle with Spring Effect */}
          <motion.div
            className="absolute bottom-0 left-1/2 w-1 h-24 origin-bottom"
            style={{
              rotate: rotation,
              translateX: "-50%",
            }}
          >
            <motion.div
              className={cn(
                "w-full h-full bg-white rounded-full shadow-lg",
                isVolatile && getGlowColor(displayScore)
              )}
              animate={isVolatile ? { scale: [1, 1.2, 1] } : {}}
              transition={{ duration: 2, repeat: Infinity }}
            />
            <motion.div
              className={cn(
                "absolute bottom-0 left-1/2 -translate-x-1/2 w-3 h-3 bg-white rounded-full shadow-lg",
                isVolatile && getGlowColor(displayScore)
              )}
              animate={isVolatile ? { scale: [1, 1.3, 1] } : {}}
              transition={{ duration: 2, repeat: Infinity }}
            />
          </motion.div>

          {/* Center dot */}
          <motion.div
            className="absolute bottom-0 left-1/2 -translate-x-1/2 w-4 h-4 bg-crypto-card rounded-full border-2 border-white"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.8, type: "spring", stiffness: 200 }}
          />
        </div>

        {/* Score display with Odometer */}
        <motion.div
          className="text-center mt-4"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.5, type: "spring" }}
        >
          <div className="flex items-center justify-center gap-3 mb-2">
            <motion.span
              className="text-5xl"
              animate={isVolatile ? { rotate: [0, 10, -10, 0] } : {}}
              transition={{ duration: 0.5, repeat: isVolatile ? Infinity : 0, repeatDelay: 1 }}
            >
              {getSentimentEmoji(displayScore)}
            </motion.span>
            <OdometerNumber
              value={displayScore}
              decimals={0}
              className={cn("text-6xl font-bold", getColor(displayScore))}
            />
          </div>
          <motion.p
            className={cn(
              "text-2xl font-semibold uppercase tracking-wide font-sf-pro",
              getColor(displayScore)
            )}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.7 }}
          >
            {sentiment}
          </motion.p>
        </motion.div>

        {/* Scale labels */}
        <motion.div
          className="flex justify-between w-64 mt-6 text-xs text-gray-500 font-medium"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.9 }}
        >
          <span>Extreme Fear</span>
          <span>Neutral</span>
          <span>Extreme Greed</span>
        </motion.div>
      </div>
    </motion.div>
  );
}
