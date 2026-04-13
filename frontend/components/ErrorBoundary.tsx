"use client";

import React from "react";

interface ErrorBoundaryProps {
	children: React.ReactNode;
	fallbackMessage?: string;
}

interface ErrorBoundaryState {
	hasError: boolean;
}

export default class ErrorBoundary extends React.Component<
	ErrorBoundaryProps,
	ErrorBoundaryState
> {
	constructor(props: ErrorBoundaryProps) {
		super(props);
		this.state = { hasError: false };
	}

	static getDerivedStateFromError(): ErrorBoundaryState {
		return { hasError: true };
	}

	componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
		console.error("[ErrorBoundary] caught:", error, errorInfo);
	}

	render() {
		if (this.state.hasError) {
			return (
				<div className="rounded-xl bg-bg-surface p-4">
					<p className="text-sm text-metric-packed">
						{this.props.fallbackMessage ??
							"Something went wrong loading this section."}
					</p>
				</div>
			);
		}
		return this.props.children;
	}
}
