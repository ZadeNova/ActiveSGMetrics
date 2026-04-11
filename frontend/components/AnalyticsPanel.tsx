"use client";
import Anomaly from "@/components/Anomaly";
import History from "@/components/History";
import Heatmap from "@/components/Heatmap";
import BestTime from "@/components/BestTime";

interface AnalyticsPanelProps {
	facilityId: string;
}

export default function AnalyticsPanel({ facilityId }: AnalyticsPanelProps) {
	return (
		<div className="flex flex-col gap-6">
			<Anomaly facilityId={facilityId} />
			<div className="grid grid-cols-2 gap-6">
				<History facilityId={facilityId} />
				<BestTime facilityId={facilityId} />
			</div>
			<Heatmap facilityId={facilityId} />
		</div>
	);
}
