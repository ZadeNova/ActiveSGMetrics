"use client";

import useSWR from "swr";
import { fetcher } from "@/lib/fetcher";
import type { AnomalyResponse } from "@/types";

interface AnomalyProps {
	facilityId: string;
}

export default function Anomaly({ facilityId }: AnomalyProps) {
	const { data, error, isLoading } = useSWR<AnomalyResponse>(
		`${process.env.NEXT_PUBLIC_API_URL}/api/v1/gyms/${facilityId}/anomaly`,
		fetcher,
	);

	if (isLoading) return <div className="text-sm text-gray-400">Loading...</div>;
	if (error)
		return (
			<div className="text-sm text-red-400">Failed to load anomaly data</div>
		);
	if (!data) return null;

	return (
		<div className="rounded-lg border p-4 flex flex-col gap-3">
			<div className="flex items-center justify-between">
				<h2 className="text-sm font-medium text-gray-500">Current Status</h2>
				{data.is_anomaly && (
					<span className="text-xs px-2 py-1 rounded-md bg-red-50 text-red-600 border border-red-200">
						{data.severity}
					</span>
				)}
			</div>

			<div className="grid grid-cols-3 gap-4">
				<div>
					<p className="text-xs text-gray-400">Current</p>
					<p className="text-2xl font-medium">
						{Math.round(data.current_occupancy)}%
					</p>
				</div>
				<div>
					<p className="text-xs text-gray-400">Historical mean</p>
					<p className="text-2xl font-medium">
						{Math.round(data.historical_mean)}%
					</p>
				</div>
				<div>
					<p className="text-xs text-gray-400">Z-score</p>
					<p className="text-2xl font-medium">{data.z_score.toFixed(1)}</p>
				</div>
			</div>
		</div>
	);
}
