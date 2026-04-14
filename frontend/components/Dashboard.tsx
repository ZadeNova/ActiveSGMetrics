"use client";

import { useState } from "react";
import GymSelector from "@/components/GymSelector";
import AnalyticsPanel from "@/components/AnalyticsPanel";
import ComparePanel from "@/components/ComparePanel";
import type { Gym } from "@/types";

interface DashboardProps {
	gyms: Gym[];
}

export default function Dashboard({ gyms }: DashboardProps) {
	const [mode, setMode] = useState<"single" | "compare">("single");
	const [selectedGymId, setSelectedGymId] = useState<string | null>(null);
	const [compareIds, setCompareIds] = useState<Set<string>>(new Set());

	const selectedGym = gyms.find((g) => g.facility_id === selectedGymId);

	return (
		<div className="flex h-screen bg-bg-base">
			<GymSelector
				gyms={gyms}
				mode={mode}
				setMode={setMode}
				selectedGymId={selectedGymId}
				onSelect={setSelectedGymId}
				compareIds={compareIds}
				setCompareIds={setCompareIds}
			/>
			<main className="flex-1 overflow-y-auto p-6">
				{mode === "compare" ? (
					compareIds.size >= 2 ? (
						<ComparePanel selectedIds={Array.from(compareIds)} gyms={gyms} />
					) : (
						<div className="flex h-full items-center justify-center text-text-muted">
							Select at least 2 gyms to compare
						</div>
					)
				) : selectedGymId && selectedGym ? (
					<AnalyticsPanel
						facilityId={selectedGymId}
						gymName={selectedGym.name}
					/>
				) : (
					<div className="flex h-full items-center justify-center text-text-muted">
						Select a gym to view analytics
					</div>
				)}
			</main>
		</div>
	);
}
