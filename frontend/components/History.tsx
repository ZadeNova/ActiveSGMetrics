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

/**
 * Formats raw ISO timestamps into clean, range-appropriate labels.
 *
 * 1D  → "2:00 PM"   (time only — all data is same day)
 * 3D  → "Mon 2 PM"  (day + short time)
 * 7D/30D → "12 Jan"  (date only — time is noise at this scale)
 */
function formatTick(timestamp: string, range: Range): string {
	const date = new Date(timestamp);
	const opts: Intl.DateTimeFormatOptions = { timeZone: "Asia/Singapore" };

	if (range === "1D") {
		return date.toLocaleTimeString("en-SG", {
			...opts,
			hour: "numeric",
			minute: "2-digit",
			hour12: true,
		});
	}
	if (range === "3D") {
		const day = date.toLocaleDateString("en-SG", { ...opts, weekday: "short" });
		const hour = date.toLocaleTimeString("en-SG", {
			...opts,
			hour: "numeric",
			hour12: true,
		});
		return `${day} ${hour}`;
	}
	return date.toLocaleDateString("en-SG", {
		...opts,
		day: "numeric",
		month: "short",
	});
}

/**
 * Computes a tick interval that prevents label overlap.
 * Wider ranges = fewer ticks.
 */
function getTickInterval(dataLength: number, range: Range): number {
	if (range === "1D") return Math.max(1, Math.floor(dataLength / 6));
	if (range === "3D") return Math.max(1, Math.floor(dataLength / 6));
	if (range === "7D") return Math.max(1, Math.floor(dataLength / 7));
	return Math.max(1, Math.floor(dataLength / 8));
}

export default function History({ facilityId }: HistoryProps) {
	const [range, setRange] = useState<Range>("1D");

	const { data, error, isLoading } = useSWR<HistoryResponse>(
		`${process.env.NEXT_PUBLIC_API_URL}/api/v1/gyms/${facilityId}/history?range=${range}`,
		fetcher,
		{ refreshInterval: 3_600_000 },
	);

	if (isLoading) {
		return (
			<div className="rounded-xl bg-bg-surface p-5">
				<p className="text-sm text-text-muted">Loading...</p>
			</div>
		);
	}
	if (error) {
		return (
			<div className="rounded-xl bg-bg-surface p-5">
				<p className="text-sm text-metric-packed">Failed to load history</p>
			</div>
		);
	}
	if (!data) return null;

	// Keep raw ISO timestamp — the formatter handles presentation
	const chartData = data.history.map((entry) => ({
		timestamp: entry.timestamp,
		occupancy: Math.round(entry.occupancy_percentage),
	}));

	return (
		<div className="rounded-xl bg-bg-surface p-5 flex flex-col gap-3">
			<div className="flex items-center justify-between">
				<h2 className="text-sm font-medium text-text-muted">
					Occupancy history
				</h2>
				<div className="flex gap-1">
					{RANGES.map((r) => (
						<button
							key={r}
							onClick={() => setRange(r)}
							className={`text-xs px-2.5 py-1 rounded-md transition-colors ${
								range === r
									? "bg-accent-primary/20 text-accent-primary"
									: "text-text-muted hover:bg-bg-surface-hover"
							}`}
						>
							{r}
						</button>
					))}
				</div>
			</div>

			<ResponsiveContainer width="100%" height={180}>
				<LineChart data={chartData}>
					<XAxis
						dataKey="timestamp"
						tick={{ fontSize: 10 }}
						tickFormatter={(val) => formatTick(val, range)}
						interval={getTickInterval(chartData.length, range)}
						stroke="var(--color-bg-surface-hover)"
					/>
					<YAxis
						domain={[0, 100]}
						tick={{ fontSize: 10 }}
						unit="%"
						width={40}
						stroke="var(--color-bg-surface-hover)"
					/>
					<Tooltip
						formatter={(value) => [`${value}%`, "Occupancy"]}
						labelFormatter={(label) => formatTick(label, range)}
						contentStyle={{
							backgroundColor: "var(--color-bg-surface)",
							borderColor: "var(--color-bg-surface-hover)",
							borderRadius: "8px",
							color: "var(--color-text-primary)",
						}}
					/>
					{/*
					  stepAfter is correct for discrete hourly snapshots.
					  monotone would imply smooth continuous transitions between readings —
					  the scraper captures a point-in-time value, nothing in between.
					*/}
					<Line
						type="stepAfter"
						dataKey="occupancy"
						stroke="var(--color-accent-primary)"
						strokeWidth={1.5}
						dot={false}
					/>
				</LineChart>
			</ResponsiveContainer>
		</div>
	);
}
