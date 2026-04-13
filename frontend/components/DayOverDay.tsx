"use client";

import useSWR from "swr";
import { fetcher } from "@/lib/fetcher";
import type { DayOverDayResponse } from "@/types";
import {
	LineChart,
	Line,
	XAxis,
	YAxis,
	Tooltip,
	Legend,
	ResponsiveContainer,
} from "recharts";

interface DayOverDayProps {
	facilityId: string;
}

const OPERATING_HOURS = Array.from({ length: 15 }, (_, i) => i + 8); // 8–22

function formatHour(hour: number): string {
	if (hour === 12) return "12p";
	return hour < 12 ? `${hour}a` : `${hour % 12}p`;
}

export default function DayOverDay({ facilityId }: DayOverDayProps) {
	const { data, error, isLoading } = useSWR<DayOverDayResponse>(
		`${process.env.NEXT_PUBLIC_API_URL}/api/v1/gyms/${facilityId}/day-over-day`,
		fetcher,
		{ refreshInterval: 7_200_000 },
	);

	if (isLoading)
		return <div className="text-sm text-text-muted">Loading...</div>;
	if (error)
		return (
			<div className="text-sm text-metric-packed">
				Failed to load day comparison.
			</div>
		);
	if (!data) return null;

	const chartData = OPERATING_HOURS.map((hour) => ({
		hour,
		today: data.today.find((r) => r.hour === hour)?.occupancy_percentage,
		lastWeek: data.last_week.find((r) => r.hour === hour)?.occupancy_percentage,
	}));

	return (
		<div className="rounded-xl bg-bg-surface p-5 flex flex-col gap-3">
			<h2 className="text-sm font-medium text-text-muted">
				Today vs. last week
			</h2>
			<ResponsiveContainer width="100%" height={160}>
				<LineChart data={chartData}>
					<XAxis
						dataKey="hour"
						tickFormatter={formatHour}
						tick={{ fontSize: 11 }}
					/>
					<YAxis domain={[0, 100]} tick={{ fontSize: 11 }} unit="%" />
					<Tooltip
						formatter={(value, name) => [
							`${Math.round(Number(value))}%`,
							name === "today" ? data.today_label : data.last_week_label,
						]}
					/>
					<Legend
						formatter={(value) =>
							value === "today" ? data.today_label : data.last_week_label
						}
						verticalAlign="top"
						align="right"
					/>
					<Line
						type="stepAfter"
						dataKey="today"
						stroke="var(--color-accent-primary)"
						strokeWidth={2}
						dot={false}
						connectNulls={false}
					/>
					<Line
						type="stepAfter"
						dataKey="lastWeek"
						stroke="var(--color-text-muted)"
						strokeWidth={1.5}
						strokeDasharray="6 3"
						dot={false}
						connectNulls={false}
					/>
				</LineChart>
			</ResponsiveContainer>
		</div>
	);
}
