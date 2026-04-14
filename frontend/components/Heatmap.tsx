"use client";

import useSWR from "swr";
import { useState } from "react";
import { fetcher } from "@/lib/fetcher";
import type { HeatmapResponse } from "@/types";
import React from "react";

interface HeatmapProps {
	facilityId: string;
}

const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
const HOURS = Array.from({ length: 15 }, (_, i) => i + 8);

function formatHour(hour: number): string {
	if (hour === 12) return "12p";
	return hour < 12 ? `${hour}a` : `${hour % 12}p`;
}

function formatHourLong(hour: number): string {
	if (hour === 0) return "12 AM";
	if (hour === 12) return "12 PM";
	return hour < 12 ? `${hour} AM` : `${hour - 12} PM`;
}

/**
 * Returns both the Tailwind class AND a readable label for the tooltip.
 */
function getCellInfo(occupancy: number): {
	bg: string;
	label: string;
	dotColor: string;
} {
	if (occupancy < 30)
		return {
			bg: "bg-metric-empty",
			label: "Quiet",
			dotColor: "bg-metric-empty",
		};
	if (occupancy < 60)
		return {
			bg: "bg-metric-normal",
			label: "Moderate",
			dotColor: "bg-metric-normal",
		};
	if (occupancy < 85)
		return { bg: "bg-metric-busy", label: "Busy", dotColor: "bg-metric-busy" };
	return {
		bg: "bg-metric-packed",
		label: "Packed",
		dotColor: "bg-metric-packed",
	};
}

function getCellOpacity(occupancy: number): string {
	if (occupancy === 0) return "opacity-10";
	if (occupancy < 30) return "opacity-50";
	if (occupancy < 60) return "opacity-70";
	if (occupancy < 85) return "opacity-85";
	return "opacity-100";
}

/** Tooltip state — tracks which cell the user is hovering. */
interface TooltipState {
	day: string;
	hour: number;
	occupancy: number;
	x: number;
	y: number;
}

export default function Heatmap({ facilityId }: HeatmapProps) {
	const [tooltip, setTooltip] = useState<TooltipState | null>(null);

	const { data, error, isLoading } = useSWR<HeatmapResponse>(
		`${process.env.NEXT_PUBLIC_API_URL}/api/v1/gyms/${facilityId}/heatmap`,
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
				<p className="text-sm text-metric-packed">Failed to load heatmap</p>
			</div>
		);
	}
	if (!data) return null;

	const lookup: Record<string, number> = {};
	data.data.forEach((entry) => {
		lookup[`${entry.day_of_week}-${entry.hour}`] = entry.avg_occupancy;
	});

	return (
		<div className="rounded-xl bg-bg-surface p-5 flex flex-col gap-4 relative">
			<div className="flex items-center justify-between">
				<h2 className="text-sm font-medium text-text-muted">Weekly heatmap</h2>
				<div className="flex items-center gap-2 text-xs text-text-muted">
					<div className="flex items-center gap-1">
						<div className="w-3 h-3 rounded-sm bg-metric-empty" />
						<span>Quiet</span>
					</div>
					<div className="flex items-center gap-1">
						<div className="w-3 h-3 rounded-sm bg-metric-normal" />
						<span>Moderate</span>
					</div>
					<div className="flex items-center gap-1">
						<div className="w-3 h-3 rounded-sm bg-metric-busy" />
						<span>Busy</span>
					</div>
					<div className="flex items-center gap-1">
						<div className="w-3 h-3 rounded-sm bg-metric-packed" />
						<span>Packed</span>
					</div>
				</div>
			</div>

			<div className="overflow-x-auto">
				<div className="grid grid-cols-[auto_repeat(15,_1fr)] gap-1 min-w-[500px]">
					{/* Hour labels */}
					<div />
					{HOURS.map((h) => (
						<div key={h} className="text-center text-[10px] text-text-muted">
							{formatHour(h)}
						</div>
					))}

					{/* Data rows */}
					{DAYS.map((day, dayIndex) => (
						<React.Fragment key={day}>
							<div className="text-xs text-text-muted flex items-center pr-2">
								{day}
							</div>
							{HOURS.map((hour) => {
								const occupancy = lookup[`${dayIndex}-${hour}`] ?? 0;
								const cellInfo = getCellInfo(occupancy);
								return (
									<div
										key={hour}
										className={[
											"h-7 rounded-sm cursor-default transition-all",
											cellInfo.bg,
											getCellOpacity(occupancy),
											"hover:ring-2 hover:ring-accent-primary/50",
										].join(" ")}
										onMouseEnter={(e) => {
											const rect = e.currentTarget.getBoundingClientRect();
											const parent = e.currentTarget
												.closest(".relative")
												?.getBoundingClientRect();
											if (parent) {
												setTooltip({
													day,
													hour,
													occupancy,
													x: rect.left - parent.left + rect.width / 2,
													y: rect.top - parent.top,
												});
											}
										}}
										onMouseLeave={() => setTooltip(null)}
									/>
								);
							})}
						</React.Fragment>
					))}
				</div>
			</div>

			{/* Custom instant tooltip — no 500ms browser delay */}
			{tooltip && (
				<div
					className="absolute z-10 pointer-events-none px-3 py-2 rounded-lg bg-bg-base border border-bg-surface-hover shadow-lg"
					style={{
						left: tooltip.x,
						top: tooltip.y,
						transform: "translate(-50%, -100%) translateY(-8px)",
					}}
				>
					<div className="flex items-center gap-2">
						<div
							className={`w-2.5 h-2.5 rounded-full ${getCellInfo(tooltip.occupancy).dotColor}`}
						/>
						<span className="text-xs font-medium text-text-primary tabular-nums">
							{Math.round(tooltip.occupancy)}%
						</span>
						<span className="text-xs text-text-muted">
							{getCellInfo(tooltip.occupancy).label}
						</span>
					</div>
					<p className="text-[10px] text-text-muted mt-0.5">
						{tooltip.day} {formatHourLong(tooltip.hour)}
					</p>
				</div>
			)}
		</div>
	);
}
