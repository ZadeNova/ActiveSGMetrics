"use client";

import useSWR from "swr";
import { fetcher } from "@/lib/fetcher";
import type { AnomalyResponse } from "@/types";

interface AnomalyProps {
	facilityId: string;
}

/**
 * Maps backend severity field to user-friendly labels.
 * Colors use the semantic metric palette from the design system.
 */
function getSeverityDisplay(severity: string, isAnomaly: boolean) {
	if (!isAnomaly) {
		return {
			label: "Normal",
			className:
				"bg-metric-empty/20 text-metric-empty border border-metric-empty/30",
		};
	}
	switch (severity.toLowerCase()) {
		case "high":
			return {
				label: "Very busy",
				className:
					"bg-metric-packed/20 text-metric-packed border border-metric-packed/30",
			};
		case "medium":
			return {
				label: "Busier than usual",
				className:
					"bg-metric-busy/20 text-metric-busy border border-metric-busy/30",
			};
		default:
			return {
				label: "Slightly busy",
				className:
					"bg-metric-normal/20 text-metric-normal border border-metric-normal/30",
			};
	}
}

/**
 * Computes relative time string from the data timestamp.
 * Since the scraper runs ~hourly, this tells the user how stale the reading is.
 */
function formatLastUpdated(timestamp: string): string {
	const updatedAt = new Date(timestamp);
	const now = new Date();
	const diffMs = now.getTime() - updatedAt.getTime();
	const diffMins = Math.floor(diffMs / 60_000);

	if (diffMins < 1) return "Just now";
	if (diffMins < 60)
		return `Updated ${diffMins} min${diffMins === 1 ? "" : "s"} ago`;

	const diffHours = Math.floor(diffMins / 60);
	if (diffHours < 24)
		return `Updated ${diffHours} hr${diffHours === 1 ? "" : "s"} ago`;

	// Stale data — show absolute SGT time so the user knows exactly when
	return updatedAt.toLocaleString("en-SG", {
		timeZone: "Asia/Singapore",
		day: "numeric",
		month: "short",
		hour: "2-digit",
		minute: "2-digit",
	});
}

export default function Anomaly({ facilityId }: AnomalyProps) {
	const { data, error, isLoading } = useSWR<AnomalyResponse>(
		`${process.env.NEXT_PUBLIC_API_URL}/api/v1/gyms/${facilityId}/anomaly`,
		fetcher,
		{ refreshInterval: 600_000 }, // 10 min — lightly polls for hourly scraper updates
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
					Failed to load current status
				</p>
			</div>
		);
	}
	if (!data) return null;

	const severity = getSeverityDisplay(data.severity, data.is_anomaly);

	return (
		<div className="rounded-xl bg-bg-surface p-5 flex flex-col gap-4">
			<div className="flex items-center justify-between">
				<h2 className="text-sm font-medium text-text-muted">
					Latest Recorded Occupancy
				</h2>
				<span className="text-xs text-text-muted">
					{formatLastUpdated(data.timestamp)}
				</span>
			</div>

			<div className="flex items-center gap-3">
				<span className="text-4xl font-semibold tabular-nums">
					{Math.round(data.current_occupancy)}%
				</span>
				<span
					className={`text-xs px-2.5 py-1 rounded-md ${severity.className}`}
				>
					{severity.label}
				</span>
			</div>

			<p className="text-sm text-text-muted">
				Usual occupancy at this hour:{" "}
				<span className="text-text-primary font-medium">
					{Math.round(data.historical_mean)}%
				</span>
			</p>
		</div>
	);
}
