"use client";

import { useState } from "react";
import useSWR from "swr";
import { fetcher } from "@/lib/fetcher";
import type {
	CompareHistoryResponse,
	CompareHeatmapResponse,
	Gym,
} from "@/types";
import {
	LineChart,
	Line,
	XAxis,
	YAxis,
	Tooltip,
	Legend,
	ResponsiveContainer,
} from "recharts";
import React from "react";

interface ComparePanelProps {
	selectedIds: string[];
	gyms: Gym[];
}

const RANGES = ["1D", "3D", "7D", "30D"] as const;
type Range = (typeof RANGES)[number];

// One colour per gym slot — matches spec
const GYM_COLORS = [
	"var(--color-accent-primary)", // #89b4fa
	"var(--color-metric-empty)", // #a6e3a1
	"var(--color-metric-busy)", // #fab387
];

const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
const HOURS = Array.from({ length: 15 }, (_, i) => i + 8); // 8–22

function formatHour(hour: number): string {
	if (hour === 12) return "12p";
	return hour < 12 ? `${hour}a` : `${hour % 12}p`;
}

function getHeatmapColor(occupancy: number): string {
	if (occupancy === 0) return "bg-bg-surface";
	if (occupancy < 25) return "bg-metric-empty/30";
	if (occupancy < 50) return "bg-metric-empty/60";
	if (occupancy < 75) return "bg-metric-normal";
	return "bg-metric-busy";
}

export default function ComparePanel({ selectedIds, gyms }: ComparePanelProps) {
	const [range, setRange] = useState<Range>("7D");

	const idsParam = selectedIds.join(",");

	const { data: historyData, error: historyError } =
		useSWR<CompareHistoryResponse>(
			`${process.env.NEXT_PUBLIC_API_URL}/api/v1/gyms/compare/history?ids=${idsParam}&range=${range}`,
			fetcher,
			{ refreshInterval: 3_600_000 },
		);

	const { data: heatmapData, error: heatmapError } =
		useSWR<CompareHeatmapResponse>(
			`${process.env.NEXT_PUBLIC_API_URL}/api/v1/gyms/compare/heatmap?ids=${idsParam}`,
			fetcher,
			{ refreshInterval: 7_200_000 },
		);

	const gymNames = selectedIds.map(
		(id) => gyms.find((g) => g.facility_id === id)?.name ?? id,
	);

	// Build merged chart data — one entry per timestamp, keyed by ISO string
	const chartData = (() => {
		if (!historyData) return [];
		const map = new Map<string, Record<string, number>>();
		historyData.gyms.forEach((series, i) => {
			series.history.forEach((record) => {
				const key = record.timestamp;
				if (!map.has(key)) map.set(key, { timestamp: new Date(key).getTime() });
				map.get(key)![`gym_${i}`] = record.occupancy_percentage;
			});
		});
		return Array.from(map.values()).sort((a, b) => a.timestamp - b.timestamp);
	})();

	const selectedGymNames = selectedIds
		.map((id) => gyms.find((g) => g.facility_id === id)?.name)
		.filter(Boolean)
		.join(", ");

	return (
		<div className="flex flex-col gap-6">
			<h1 className="text-xl font-semibold text-text-primary">
				Comparing: {selectedGymNames}
			</h1>

			{/* Overlaid history chart */}
			<div className="rounded-xl bg-bg-surface p-5 flex flex-col gap-3">
				<div className="flex items-center justify-between">
					<h2 className="text-sm font-medium text-text-muted">
						Occupancy comparison
					</h2>
					<div className="flex gap-1">
						{RANGES.map((r) => (
							<button
								key={r}
								onClick={() => setRange(r)}
								className={`text-xs px-2 py-1 rounded-md border transition-colors ${
									range === r
										? "bg-bg-surface-hover text-text-primary border-bg-surface-hover"
										: "text-text-muted border-transparent hover:border-bg-surface-hover"
								}`}
							>
								{r}
							</button>
						))}
					</div>
				</div>

				{historyError ? (
					<div className="text-sm text-metric-packed">
						Failed to load comparison history.
					</div>
				) : !historyData ? (
					<div className="text-sm text-text-muted">Loading...</div>
				) : (
					<ResponsiveContainer width="100%" height={200}>
						<LineChart data={chartData}>
							<XAxis
								dataKey="timestamp"
								tickFormatter={(ts) =>
									new Date(ts).toLocaleTimeString("en-SG", {
										hour: "2-digit",
										minute: "2-digit",
										timeZone: "Asia/Singapore",
									})
								}
								tick={{ fontSize: 11 }}
								interval="preserveStartEnd"
							/>
							<YAxis domain={[0, 100]} tick={{ fontSize: 11 }} unit="%" />
							<Tooltip
								labelFormatter={(ts) =>
									new Date(ts).toLocaleString("en-SG", {
										timeZone: "Asia/Singapore",
									})
								}
								formatter={(value, name) => {
									const idx = parseInt((name as string).replace("gym_", ""));
									return [`${Math.round(Number(value))}%`, gymNames[idx]];
								}}
							/>
							<Legend
								formatter={(value) => {
									const idx = parseInt(value.replace("gym_", ""));
									return gymNames[idx];
								}}
							/>
							{selectedIds.map((_, i) => (
								<Line
									key={i}
									type="stepAfter"
									dataKey={`gym_${i}`}
									stroke={GYM_COLORS[i]}
									strokeWidth={1.5}
									dot={false}
									connectNulls={false}
								/>
							))}
						</LineChart>
					</ResponsiveContainer>
				)}
			</div>

			{/* Side-by-side heatmaps */}
			<div
				className={`grid gap-4 ${
					selectedIds.length === 2 ? "grid-cols-2" : "grid-cols-3"
				}`}
			>
				{heatmapError ? (
					<div className="text-sm text-metric-packed col-span-full">
						Failed to load heatmaps.
					</div>
				) : !heatmapData ? (
					<div className="text-sm text-text-muted col-span-full">
						Loading...
					</div>
				) : (
					heatmapData.gyms.map((series, gymIdx) => {
						const lookup: Record<string, number> = {};
						series.data.forEach((cell) => {
							lookup[`${cell.day_of_week}-${cell.hour}`] = cell.avg_occupancy;
						});

						return (
							<div
								key={series.facility_id}
								className="rounded-xl bg-bg-surface p-4 flex flex-col gap-2"
							>
								<h3
									className="text-xs font-medium truncate"
									style={{ color: GYM_COLORS[gymIdx] }}
								>
									{series.name}
								</h3>
								<div className="overflow-x-auto">
									<div className="grid grid-cols-[32px_repeat(15,_1fr)] gap-0.5 min-w-[320px]">
										<div />
										{HOURS.map((h) => (
											<div
												key={h}
												className="text-center text-[9px] text-text-muted"
											>
												{formatHour(h)}
											</div>
										))}
										{DAYS.map((day, dayIndex) => (
											<React.Fragment key={day}>
												<div className="text-[10px] text-text-muted flex items-center">
													{day}
												</div>
												{HOURS.map((hour) => {
													const occupancy = lookup[`${dayIndex}-${hour}`] ?? 0;
													return (
														<div
															key={hour}
															title={`${Math.round(occupancy)}%`}
															className={`h-5 rounded-sm ${getHeatmapColor(occupancy)}`}
														/>
													);
												})}
											</React.Fragment>
										))}
									</div>
								</div>
							</div>
						);
					})
				)}
			</div>
		</div>
	);
}
