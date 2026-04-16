"use client";

interface MetricCardProps {
    title: string;
    value: number;
    trend: string;
    trendPositive?: boolean;
    sparklineData?: number[];
    className?: string;
}

function Sparkline({ data, color = "#3b82f6" }: { data: number[]; color?: string }) {
    const width = 80;
    const height = 32;
    const padding = 2;

    const min = Math.min(...data);
    const max = Math.max(...data);
    const range = max - min || 1;

    const points = data.map((value, i) => {
        const x = padding + (i / (data.length - 1)) * (width - padding * 2);
        const y = height - padding - ((value - min) / range) * (height - padding * 2);
        return `${x},${y}`;
    });

    const pathD = `M ${points.join(" L ")}`;

    const firstX = padding;
    const lastX = padding + ((data.length - 1) / (data.length - 1)) * (width - padding * 2);
    const areaD = `${pathD} L ${lastX},${height} L ${firstX},${height} Z`;

    return (
        <svg
            className="shrink-0"
            width={width}
            height={height}
            viewBox={`0 0 ${width} ${height}`}
        >
            <defs>
                <linearGradient id={`sparkline-gradient-${color.replace("#", "")}`} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor={color} stopOpacity="0.15" />
                    <stop offset="100%" stopColor={color} stopOpacity="0" />
                </linearGradient>
            </defs>
            <path
                d={areaD}
                fill={`url(#sparkline-gradient-${color.replace("#", "")})`}
            />
            <path
                d={pathD}
                fill="none"
                stroke={color}
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
            />
        </svg>
    );
}

export default function MetricCard({
    title,
    value,
    trend,
    trendPositive = true,
    sparklineData = [40, 45, 42, 55, 58, 62, 65, 70],
    className = "",
}: MetricCardProps) {
    return (
        <div className={`bg-white border border-gray-200 rounded-xl p-6 flex flex-col gap-2 transition-all duration-300 hover:shadow-lg hover:shadow-blue-100/60 hover:border-blue-200 hover:-translate-y-0.5 ${className}`}>
            <span className="text-sm font-medium text-gray-500">{title}</span>
            <div className="flex items-end justify-between">
                <div>
                    <div className="text-4xl font-bold text-gray-800 leading-none">{value}</div>
                    <div className={`text-sm font-medium mt-1 ${trendPositive ? "text-green-500" : "text-red-500"}`}>
                        {trend}
                    </div>
                </div>
                <Sparkline data={sparklineData} />
            </div>
        </div>
    );
}
