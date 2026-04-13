"use client";

import useSWR from "swr";
import { fetcher } from "@/lib/fetcher";
import type { BestTimeResponse } from "@/types";

interface BestTimeProps {
	facilityId: string;
}

const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

function formatDay(day: number): string {
	return DAYS[day];
}

function formatHour(hour: number): string {
	if (hour === 0) return "12 AM";
	if (hour === 12) return "12 PM";
	return hour < 12 ? `${hour} AM` : `${hour % 12} PM`;
}

export default function BestTime({ facilityId }: BestTimeProps) {
	const { data, error, isLoading } = useSWR<BestTimeResponse>(
		`${process.env.NEXT_PUBLIC_API_URL}/api/v1/gyms/${facilityId}/best-time`,
		fetcher,
		{ refreshInterval: 7_200_000 },
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
				<p className="text-sm text-metric-packed">
					Failed to load quietest slots
				</p>
			</div>
		);
	}
	if (!data) return null;

	// Scale bars relative to the max value, not 100%
	const maxOccupancy = Math.max(
		...data.quietest_slots.map((s) => s.avg_occupancy),
		1,
	);

	return (
		<div className="rounded-xl bg-bg-surface p-5 flex flex-col gap-3">
			<h2 className="text-sm font-medium text-text-muted">
				Typically quietest slots
			</h2>
			<div className="flex flex-col gap-2.5">
				{data.quietest_slots.map((slot, index) => (
					<div key={index} className="flex items-center gap-3">
						<span className="text-sm w-24 text-text-muted shrink-0">
							{formatDay(slot.day_of_week)} {formatHour(slot.hour)}
						</span>
						<div className="flex-1 h-2 bg-bg-surface-hover rounded-full overflow-hidden">
							<div
								className="h-full bg-metric-empty rounded-full transition-all duration-300"
								style={{
									width: `${(slot.avg_occupancy / maxOccupancy) * 100}%`,
								}}
							/>
						</div>
						<span className="text-xs text-text-muted w-10 text-right tabular-nums">
							{Math.round(slot.avg_occupancy)}%
						</span>
					</div>
				))}
			</div>
		</div>
	);
}
