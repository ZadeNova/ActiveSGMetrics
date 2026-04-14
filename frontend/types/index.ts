// types/index.ts

export interface Gym {
	facility_id: string;
	name: string;
	facility_type: string;
}

export interface OccupancyRecord {
	timestamp: string;
	occupancy_percentage: number;
	is_closed: boolean;
}

export interface HistoryResponse {
	facility_id: string;
	name: string;
	history: OccupancyRecord[];
}

export interface HeatmapEntry {
	day_of_week: number;
	hour: number;
	avg_occupancy: number;
}

export interface HeatmapResponse {
	facility_id: string;
	name: string;
	data: HeatmapEntry[];
}

export interface BestTimeSlot {
	day_of_week: number;
	hour: number;
	avg_occupancy: number;
}

export interface BestTimeResponse {
	facility_id: string;
	name: string;
	quietest_slots: BestTimeSlot[];
}

export interface AnomalyResponse {
	facility_id: string;
	name: string;
	is_anomaly: boolean;
	current_occupancy: number;
	historical_mean: number;
	z_score: number;
	severity: string;
	timestamp: string;
	day_of_week: number;
	hour: number;
}

export interface HourlyReading {
	hour: number;
	occupancy_percentage: number;
}

export interface DayOverDayResponse {
	facility_id: string;
	name: string;
	today_label: string;
	last_week_label: string;
	today: HourlyReading[];
	last_week: HourlyReading[];
}

export interface GymHistorySeries {
	facility_id: string;
	name: string;
	history: OccupancyRecord[]; // reuse existing
}

export interface CompareHistoryResponse {
	gyms: GymHistorySeries[];
}

export interface GymHeatmapSeries {
	facility_id: string;
	name: string;
	data: HeatmapEntry[]; // reuse existing
}

export interface CompareHeatmapResponse {
	gyms: GymHeatmapSeries[];
}
