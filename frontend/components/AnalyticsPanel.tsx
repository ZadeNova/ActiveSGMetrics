"use client";

import Anomaly from "@/components/Anomaly";
import History from "@/components/History";
import Heatmap from "@/components/Heatmap";
import BestTime from "@/components/BestTime";
import ErrorBoundary from "@/components/ErrorBoundary";

interface AnalyticsPanelProps {
	facilityId: string;
	gymName: string;
}

export default function AnalyticsPanel({
	facilityId,
	gymName,
}: AnalyticsPanelProps) {
	return (
		<div className="flex flex-col gap-6">
			<h1 className="text-xl font-semibold text-text-primary">{gymName}</h1>

			<ErrorBoundary fallbackMessage="Failed to load current status.">
				<Anomaly facilityId={facilityId} />
			</ErrorBoundary>

			<div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
				<ErrorBoundary fallbackMessage="Failed to load occupancy history.">
					<History facilityId={facilityId} />
				</ErrorBoundary>
				<ErrorBoundary fallbackMessage="Failed to load quietest slots.">
					<BestTime facilityId={facilityId} />
				</ErrorBoundary>
			</div>

			<ErrorBoundary fallbackMessage="Failed to load heatmap.">
				<Heatmap facilityId={facilityId} />
			</ErrorBoundary>
		</div>
	);
}
