"use client";

import type { Gym } from "@/types";

interface GymSelectorProps {
	gyms: Gym[];
	selectedGymId: string | null;
	onSelect: (id: string) => void;
}

export default function GymSelector({
	gyms,
	selectedGymId,
	onSelect,
}: GymSelectorProps) {
	return (
		<aside
			className={[
				"w-64 h-screen overflow-y-auto border-r border-bg-surface bg-bg-base p-4 flex flex-col gap-1",
				// Custom slim scrollbar — webkit-only but covers Chrome/Edge/Safari
				"[&::-webkit-scrollbar]:w-1.5",
				"[&::-webkit-scrollbar-track]:bg-transparent",
				"[&::-webkit-scrollbar-thumb]:bg-bg-surface-hover",
				"[&::-webkit-scrollbar-thumb]:rounded-full",
			].join(" ")}
		>
			<h2 className="text-xs font-semibold uppercase tracking-wider text-text-muted mb-3">
				Facilities
			</h2>
			{gyms.map((gym) => {
				const isSelected = selectedGymId === gym.facility_id;
				return (
					<button
						key={gym.facility_id}
						onClick={() => onSelect(gym.facility_id)}
						className={`text-left px-3 py-2 rounded-md text-sm transition-colors ${
							isSelected
								? "bg-bg-surface-hover text-accent-primary border-l-4 border-accent-primary font-medium"
								: "text-text-muted hover:bg-bg-surface-hover"
						}`}
					>
						{gym.name}
					</button>
				);
			})}
		</aside>
	);
}
