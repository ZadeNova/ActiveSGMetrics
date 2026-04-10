//A single shared fetcher function passed to all use useSWR() calls.
// SWR requires a fetcher - it handles caching , deduplication and revalidation
// but delegates the actual HTTP call to this function

export const fetcher = (url: string) =>
	fetch(url).then((res) => {
		// fetch() only rejects on network failure( no internet)
		// a 404 or 500 from the server is still a 'sucessful' fetch response
		// We manually throw so SWR sets its 'error' state instead of silently
		// returning bad data to our components
		if (!res.ok) throw new Error(`HTTP error: ${res.status}`);
		return res.json();
	});
