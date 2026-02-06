import { cn } from "../utils/cn";

interface SentimentGaugeProps {
  score: number;
  sentiment: string;
}

export function SentimentGauge({ score, sentiment }: SentimentGaugeProps) {
  // Calculate color based on score (0-100)
  const getColor = (score: number) => {
    if (score < 30) return "text-fear-red";
    if (score < 45) return "text-orange-500";
    if (score < 55) return "text-neutral-yellow";
    if (score < 70) return "text-lime-500";
    return "text-greed-green";
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

  // Calculate rotation for the gauge needle (-90deg to 90deg)
  const rotation = (score / 100) * 180 - 90;

  return (
    <div className={cn(
      "relative overflow-hidden rounded-2xl border border-crypto-border",
      "bg-gradient-to-br p-8",
      getBackgroundColor(score)
    )}>
      {/* Header */}
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-white mb-2">Fear & Greed Index</h2>
        <p className="text-gray-400 text-sm">Live Crypto Market Sentiment</p>
      </div>

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
            </defs>
            {/* Background arc */}
            <path
              d="M 20 90 A 80 80 0 0 1 180 90"
              fill="none"
              stroke="url(#gaugeGradient)"
              strokeWidth="20"
              strokeLinecap="round"
              opacity="0.3"
            />
            {/* Active arc */}
            <path
              d="M 20 90 A 80 80 0 0 1 180 90"
              fill="none"
              stroke="url(#gaugeGradient)"
              strokeWidth="20"
              strokeLinecap="round"
              strokeDasharray={`${(score / 100) * 251.2} 251.2`}
            />
          </svg>

          {/* Needle */}
          <div
            className="absolute bottom-0 left-1/2 w-1 h-24 origin-bottom transition-transform duration-1000 ease-out"
            style={{
              transform: `translateX(-50%) rotate(${rotation}deg)`,
            }}
          >
            <div className="w-full h-full bg-white rounded-full shadow-lg" />
            <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-3 h-3 bg-white rounded-full shadow-lg" />
          </div>

          {/* Center dot */}
          <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-4 h-4 bg-crypto-card rounded-full border-2 border-white" />
        </div>

        {/* Score display */}
        <div className="text-center mt-4">
          <div className="flex items-center justify-center gap-3 mb-2">
            <span className="text-5xl">{getSentimentEmoji(score)}</span>
            <span className={cn("text-6xl font-bold tabular-nums", getColor(score))}>
              {Math.round(score)}
            </span>
          </div>
          <p className={cn("text-2xl font-semibold uppercase tracking-wide", getColor(score))}>
            {sentiment}
          </p>
        </div>

        {/* Scale labels */}
        <div className="flex justify-between w-64 mt-6 text-xs text-gray-500">
          <span>Extreme Fear</span>
          <span>Neutral</span>
          <span>Extreme Greed</span>
        </div>
      </div>
    </div>
  );
}
