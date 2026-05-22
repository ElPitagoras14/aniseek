import { createFileRoute } from "@tanstack/react-router";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
	Card,
	CardContent,
	CardDescription,
	CardFooter,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";

export const Route = createFileRoute("/")({ component: Home });

function Home() {
	return (
		<div className="min-h-screen bg-background p-8">
			<div className="mx-auto max-w-2xl space-y-6">
				<div className="space-y-1">
					<div className="flex items-center gap-2">
						<h1 className="text-3xl font-bold tracking-tight text-foreground">
							AniSeek
						</h1>
						<Badge variant="secondary">Beta</Badge>
					</div>
					<p className="text-muted-foreground">
						Plataforma de streaming y descarga de anime.
					</p>
				</div>

				<div className="grid gap-4 sm:grid-cols-2">
					<Card>
						<CardHeader>
							<CardTitle>Explorar</CardTitle>
							<CardDescription>
								Busca entre miles de series y películas.
							</CardDescription>
						</CardHeader>
						<CardContent>
							<p className="text-sm text-muted-foreground">
								Accede al catálogo completo con filtros por género, estado y
								temporada.
							</p>
						</CardContent>
						<CardFooter>
							<Button className="w-full">Ver catálogo</Button>
						</CardFooter>
					</Card>

					<Card>
						<CardHeader>
							<CardTitle>Mis descargas</CardTitle>
							<CardDescription>
								Administra tus episodios descargados.
							</CardDescription>
						</CardHeader>
						<CardContent>
							<p className="text-sm text-muted-foreground">
								Descarga episodios en alta calidad para verlos sin conexión.
							</p>
						</CardContent>
						<CardFooter className="gap-2">
							<Button variant="outline" className="w-full">
								Ver lista
							</Button>
						</CardFooter>
					</Card>
				</div>

				<Card>
					<CardHeader>
						<div className="flex items-center justify-between">
							<CardTitle>Últimos episodios</CardTitle>
							<Badge>Nuevo</Badge>
						</div>
						<CardDescription>Episodios añadidos recientemente.</CardDescription>
					</CardHeader>
					<CardContent className="space-y-2">
						{["Attack on Titan", "Jujutsu Kaisen", "Chainsaw Man"].map(
							(title) => (
								<div
									key={title}
									className="flex items-center justify-between rounded-md border border-border px-3 py-2"
								>
									<span className="text-sm font-medium">{title}</span>
									<Button size="sm" variant="ghost">
										Ver
									</Button>
								</div>
							),
						)}
					</CardContent>
				</Card>
			</div>
		</div>
	);
}
