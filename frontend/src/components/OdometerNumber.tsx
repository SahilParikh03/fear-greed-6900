import { useEffect, useState } from "react";
import { motion, useSpring, useTransform } from "framer-motion";

interface OdometerNumberProps {
  value: number;
  decimals?: number;
  className?: string;
  prefix?: string;
  suffix?: string;
}

export function OdometerNumber({
  value,
  decimals = 0,
  className = "",
  prefix = "",
  suffix = "",
}: OdometerNumberProps) {
  const [displayValue, setDisplayValue] = useState(value);

  // Spring animation for smooth transitions
  const spring = useSpring(displayValue, {
    damping: 30,
    stiffness: 100,
  });

  const display = useTransform(spring, (current) =>
    current.toFixed(decimals)
  );

  useEffect(() => {
    setDisplayValue(value);
    spring.set(value);
  }, [value, spring]);

  return (
    <motion.span
      className={`tabular-nums ${className}`}
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      {prefix}
      <motion.span>{display}</motion.span>
      {suffix}
    </motion.span>
  );
}
