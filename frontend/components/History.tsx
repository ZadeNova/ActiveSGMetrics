"use client";

import useSWR from "swr";
import { useState } from "react";
import { fetcher } from "@/lib/fetcher";
import type { HistoryResponse } from "@/types";
import {
	LineChart,
	Line,
	XAxis,
	YAxis,
	Tooltip,
	ResponsiveContainer,
} from "recharts";

interface HistoryProps {
	facilityId: string;
}

const RANGES = ["1D", "3D", "7D", "30D"] as const;
type Range = (typeof RANGES)[number];

export default function History({ facilityId }: HistoryProps) {
	const [range, setRange] = useState<Range>("1D");

	const { data, error, isLoading } = useSWR<HistoryResponse>(
		`${process.env.NEXT_PUBLIC_API_URL}/api/v1/gyms/${facilityId}/history?range=${range}`,
		fetcher,
	);

	if (isLoading) return <div className="text-sm text-gray-400">Loading...</div>;
	if (error)
		return <div className="text-sm text-red-400">Failed to load history</div>;
	if (!data) return null;

	const chartData = data.history.map((entry) => ({
		time: new Date(entry.timestamp).toLocaleTimeString("en-SG", {
			hour: "2-digit",
			minute: "2-digit",
			timeZone: "Asia/Singapore", // explicit — never rely on system timezone
		}),
		occupancy: Math.round(entry.occupancy_percentage),
	}));

	return (
		<div className="rounded-lg border p-4 flex flex-col gap-3">
			<div className="flex items-center justify-between">
				<h2 className="text-sm font-medium text-gray-500">Occupancy history</h2>
				<div className="flex gap-1">
					{RANGES.map((r) => (
						<button
							key={r}
							onClick={() => setRange(r)}
							className={`text-xs px-2 py-1 rounded-md border transition-colors ${
								range === r
									? "bg-gray-100 text-gray-900 border-gray-300"
									: "text-gray-400 border-transparent hover:border-gray-200"
							}`}
						>
							{r}
						</button>
					))}
				</div>
			</div>

			<ResponsiveContainer width="100%" height={160}>
				<LineChart data={chartData}>
					<XAxis
						dataKey="time"
						tick={{ fontSize: 11 }}
						interval="preserveStartEnd"
					/>
					<YAxis domain={[0, 100]} tick={{ fontSize: 11 }} unit="%" />
					<Tooltip formatter={(value) => [`${value}%`, "Occupancy"]} />
					<Line
						type="monotone"
						dataKey="occupancy"
						stroke="#1D9E75"
						strokeWidth={1.5}
						dot={false}
					/>
				</LineChart>
			</ResponsiveContainer>
		</div>
	);
}
