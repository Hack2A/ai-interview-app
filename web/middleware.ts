import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Define all protected routes here - easier to maintain
const PROTECTED_ROUTES = [
	"/home",
	"/profile",
	"/dashboard",
	"/settings",
	"/reports",
	"/support",
	"/notifications",
	"/career",
	"/interview",
];

export function middleware(req: NextRequest) {
	const token = req.cookies.get("token");
	const { pathname } = req.nextUrl;

	// Check if user is trying to access protected routes
	const isProtectedRoute = PROTECTED_ROUTES.some((route) =>
		pathname.startsWith(route),
	);

	// If accessing protected route without token, redirect to login
	if (isProtectedRoute && !token) {
		const loginUrl = new URL("/login", req.url);
		loginUrl.searchParams.set("redirect", pathname);
		return NextResponse.redirect(loginUrl);
	}

	// If logged in and trying to access auth pages, redirect to home
	if (token && (pathname === "/login" || pathname === "/register")) {
		return NextResponse.redirect(new URL("/home", req.url));
	}

	return NextResponse.next();
}

export const config = {
	matcher: [
		/*
		 * Match all request paths except for the ones starting with:
		 * - api (API routes)
		 * - _next/static (static files)
		 * - _next/image (image optimization files)
		 * - favicon.ico (favicon file)
		 */
		'/((?!api|_next/static|_next/image|favicon.ico).*)',
	],
};
