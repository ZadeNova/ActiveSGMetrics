"use client";

import type { Gym } from "@/types";

interface GymSelectorProps {
	gyms: Gym[];
	mode: "single" | "compare";
	setMode: (mode: "single" | "compare") => void;
	selectedGymId: string | null;
	onSelect: (id: string) => void;
	compareIds: Set<string>;
	setCompareIds: (ids: Set<string>) => void;
}

export default function GymSelector({
	gyms,
	mode,
	setMode,
	selectedGymId,
	onSelect,
	compareIds,
	setCompareIds,
}: GymSelectorProps) {
	const toggleCompare = (id: string) => {
		const next = new Set(compareIds);
		if (next.has(id)) {
			next.delete(id);
		} else {
			next.add(id);
		}
		setCompareIds(next);
	};

	const atMax = compareIds.size >= 3;

	return (
		<aside
			className={[
				"w-64 h-screen overflow-y-auto border-r border-bg-surface bg-bg-base p-4 flex flex-col gap-1",
				"[&::-webkit-scrollbar]:w-1.5",
				"[&::-webkit-scrollbar-track]:bg-transparent",
				"[&::-webkit-scrollbar-thumb]:bg-bg-surface-hover",
				"[&::-webkit-scrollbar-thumb]:rounded-full",
			].join(" ")}
		>
			{/* Header row */}
			<div className="flex items-center justify-between mb-3">
				<h2 className="text-xs font-semibold uppercase tracking-wider text-text-muted">
					Facilities
				</h2>
				<button
					onClick={() => setMode(mode === "single" ? "compare" : "single")}
					className="text-xs text-accent-primary hover:underline"
				>
					{mode === "single" ? "Compare" : "← Back"}
				</button>
			</div>

			{/* Compare mode: selected count */}
			{mode === "compare" && (
				<p className="text-xs text-text-muted mb-2">
					{compareIds.size} of 3 selected
				</p>
			)}

			{/* Gym list */}
			{gyms.map((gym) => {
				if (mode === "compare") {
					const isChecked = compareIds.has(gym.facility_id);
					const isDisabled = atMax && !isChecked;

					return (
						<button
							key={gym.facility_id}
							onClick={() => !isDisabled && toggleCompare(gym.facility_id)}
							disabled={isDisabled}
							className={`text-left px-3 py-2 rounded-md text-sm transition-colors flex items-center gap-2 ${
								isChecked
									? "bg-bg-surface-hover text-accent-primary font-medium"
									: isDisabled
										? "text-text-muted opacity-40 cursor-not-allowed"
										: "text-text-muted hover:bg-bg-surface-hover"
							}`}
						>
							<span
								className={`w-4 h-4 rounded border flex-shrink-0 flex items-center justify-center text-xs ${
									isChecked
										? "bg-accent-primary border-accent-primary text-bg-base"
										: "border-bg-surface-hover"
								}`}
							>
								{isChecked && "✓"}
							</span>
							{gym.name}
						</button>
					);
				}

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
