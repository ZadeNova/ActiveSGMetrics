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
		<aside className="w-64 h-screen overflow-y-auto border-r p-4 flex flex-col gap-2">
			<h2 className="text-sm font-medium text-gray-500 mb-2">Gyms</h2>
			{gyms.map((gym) => (
				<button
					key={gym.facility_id}
					onClick={() => onSelect(gym.facility_id)}
					className={`text-left px-3 py-2 rounded-md text-sm transition-colors ${
						selectedGymId === gym.facility_id
							? "bg-gray-100 font-medium text-gray-900"
							: "text-gray-600 hover:bg-gray-50"
					}`}
				>
					{gym.name}
				</button>
			))}
		</aside>
	);
}
