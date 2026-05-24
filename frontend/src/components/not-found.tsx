import { Link } from "@tanstack/react-router";
import { useAuth } from "@/auth";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AppSidebar } from "@/features/root/components/app-sidebar";
import { MobileHeader } from "@/features/root/components/mobile-header";

export function NotFoundContent() {
	return (
		<div className="flex min-h-screen items-center justify-center bg-background">
			<Card className="max-w-md w-full rounded-2xl shadow-lg">
				<CardContent className="p-8 flex flex-col items-center text-center">
					<h1 className="text-2xl font-semibold text-foreground">
						404 - Página no encontrada
					</h1>
					<p className="mt-2 text-sm text-muted-foreground">
						Esta página está en una reunión que nunca termina.
						<br />
						Mientras tanto, puedes volver al inicio.
					</p>
					<Button variant="link" asChild className="mt-4 text-sm">
						<Link to="/">Volver al inicio</Link>
					</Button>
				</CardContent>
			</Card>
		</div>
	);
}

export function NotFound() {
	const { isAuthenticated } = useAuth();

	if (!isAuthenticated) {
		return <NotFoundContent />;
	}

	return (
		<SidebarProvider>
			<TooltipProvider>
				<AppSidebar variant="sidebar" />
				<SidebarInset>
					<MobileHeader />
					<NotFoundContent />
				</SidebarInset>
			</TooltipProvider>
		</SidebarProvider>
	);
}
