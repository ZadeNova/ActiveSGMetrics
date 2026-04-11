"use client";

import { useState } from "react";
import GymSelector from "@/components/GymSelector";
import AnalyticsPanel from "@/components/AnalyticsPanel";
import type { Gym } from "@/types";

interface DashboardProps {
	gyms: Gym[];
}

export default function Dashboard({ gyms }: DashboardProps) {
	const [selectedGymId, setSelectedGymId] = useState<string | null>(null);

	return (
		<div className="flex h-screen">
			<GymSelector
				gyms={gyms}
				selectedGymId={selectedGymId}
				onSelect={setSelectedGymId}
			/>
			<main className="flex-1 overflow-y-auto p-6">
				{selectedGymId ? (
					<AnalyticsPanel facilityId={selectedGymId} />
				) : (
					<div className="flex h-full items-center justify-center text-gray-400">
						Select a gym to view analytics
					</div>
				)}
			</main>
		</div>
	);
}
