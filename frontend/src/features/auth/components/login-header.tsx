import { Link } from "@tanstack/react-router";
import { Clapperboard } from "lucide-react";

export function LoginHeader() {
	return (
		<div className="flex flex-col items-center gap-2 text-center">
			<Clapperboard className="size-10 text-muted-foreground" />
			<h1 className="text-2xl font-bold tracking-tight">Welcome to Ani Seek</h1>
			<p className="text-sm text-muted-foreground">
				A simple way to scrap anime
			</p>
			<p className="text-sm text-muted-foreground">
				Don&apos;t have an account?{" "}
				<Link
					to="/register"
					className="text-primary underline-offset-4 hover:underline"
				>
					Sign up
				</Link>
			</p>
		</div>
	);
}
