"use client";

import useSWR from "swr";
import { fetcher } from "@/lib/fetcher";
import type { HeatmapResponse } from "@/types";
import React from "react";

interface HeatmapProps {
	facilityId: string;
}

const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
const HOURS = Array.from({ length: 24 }, (_, i) => i);

function formatHour(hour: number): string {
	if (hour === 0) return "12a";
	if (hour === 12) return "12p";
	return hour < 12 ? `${hour}a` : `${hour % 12}p`;
}

function getColor(occupancy: number): string {
	if (occupancy === 0) return "bg-gray-50";
	if (occupancy < 25) return "bg-teal-100";
	if (occupancy < 50) return "bg-teal-300";
	if (occupancy < 75) return "bg-teal-500";
	return "bg-teal-700";
}

export default function Heatmap({ facilityId }: HeatmapProps) {
	const { data, error, isLoading } = useSWR<HeatmapResponse>(
		`${process.env.NEXT_PUBLIC_API_URL}/api/v1/gyms/${facilityId}/heatmap`,
		fetcher,
	);

	if (isLoading) return <div className="text-sm text-gray-400">Loading...</div>;
	if (error)
		return <div className="text-sm text-red-400">Failed to load heatmap</div>;
	if (!data) return null;

	// Build O(1) lookup map
	const lookup: Record<string, number> = {};
	data.data.forEach((entry) => {
		lookup[`${entry.day_of_week}-${entry.hour}`] = entry.avg_occupancy;
	});

	return (
		<div className="rounded-lg border p-4 flex flex-col gap-3">
			<div className="flex items-center justify-between">
				<h2 className="text-sm font-medium text-gray-500">Weekly heatmap</h2>
				<div className="flex items-center gap-1 text-xs text-gray-400">
					<span>Quiet</span>
					{["bg-teal-100", "bg-teal-300", "bg-teal-500", "bg-teal-700"].map(
						(c) => (
							<div key={c} className={`w-4 h-4 rounded-sm ${c}`} />
						),
					)}
					<span>Busy</span>
				</div>
			</div>

			<div className="overflow-x-auto">
				<div className="grid grid-cols-[48px_repeat(24,_1fr)] gap-1 min-w-[600px]">
					<div />
					{HOURS.map((h) => (
						<div key={h} className="text-center text-[10px] text-gray-400">
							{formatHour(h)}
						</div>
					))}
					{DAYS.map((day, dayIndex) => (
						<React.Fragment key={day}>
							<div className="text-xs text-gray-400 flex items-center">
								{day}
							</div>
							{HOURS.map((hour) => {
								const occupancy = lookup[`${dayIndex}-${hour}`] ?? 0;
								return (
									<div
										key={hour}
										title={`${Math.round(occupancy)}%`}
										className={`h-6 rounded-sm ${getColor(occupancy)}`}
									/>
								);
							})}
						</React.Fragment>
					))}
				</div>
			</div>
		</div>
	);
}
