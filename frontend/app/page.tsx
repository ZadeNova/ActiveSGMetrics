import Dashboard from "@/components/Dashboard";
import type { Gym } from "@/types";

async function getGyms(): Promise<Gym[]> {
	const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/gyms`, {
		next: { revalidate: 7200 },
	});
	if (!res.ok) throw new Error("Failed to fetch gyms");
	return res.json();
}

export default async function Home() {
	const gyms = await getGyms(); // waits for the data, THEN renders
	return <Dashboard gyms={gyms} />;
}
