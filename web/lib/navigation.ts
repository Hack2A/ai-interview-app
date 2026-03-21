"use client";

import { useRouter } from "next/navigation";

let routerRef: ReturnType<typeof useRouter> | null = null;

export function RouterProvider() {
	routerRef = useRouter();
	return null;
}

export function navigate(path: string, replace = false) {
	if (!routerRef) return;

	replace ? routerRef.replace(path) : routerRef.push(path);
}
