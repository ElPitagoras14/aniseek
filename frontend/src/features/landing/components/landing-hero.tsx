import { useEffect, useState } from "react";
import { Link } from "@tanstack/react-router";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";

const PHRASES = [
	"search any anime",
	"download episodes",
	"track airing shows",
	"manage your library",
];

function useTypewriter(phrases: string[]) {
	const [displayText, setDisplayText] = useState("");
	const [phraseIndex, setPhraseIndex] = useState(0);
	const [phase, setPhase] = useState<"typing" | "pausing" | "deleting">(
		"typing",
	);

	useEffect(() => {
		const current = phrases[phraseIndex];

		if (phase === "typing") {
			if (displayText.length < current.length) {
				const t = setTimeout(
					() => setDisplayText(current.slice(0, displayText.length + 1)),
					75,
				);
				return () => clearTimeout(t);
			}
			const t = setTimeout(() => setPhase("deleting"), 2000);
			return () => clearTimeout(t);
		}

		if (phase === "deleting") {
			if (displayText.length > 0) {
				const t = setTimeout(
					() => setDisplayText(current.slice(0, displayText.length - 1)),
					35,
				);
				return () => clearTimeout(t);
			}
			setPhraseIndex((i) => (i + 1) % phrases.length);
			setPhase("typing");
		}
	}, [displayText, phase, phraseIndex, phrases]);

	return displayText;
}

export function LandingHero() {
	const typewriterText = useTypewriter(PHRASES);

	return (
		<section className="relative overflow-hidden py-24 md:py-36">
			<div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-primary/10 to-transparent" />
			<div className="relative mx-auto w-full max-w-6xl px-4 text-center md:px-6 lg:px-8">
				<h1 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl">
					Find it. Download it. Watch it.
				</h1>
				<p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground">
					Search, download, and manage anime from multiple sources. All in one
					clean, fast dashboard. No subscriptions, no paywalls.
				</p>
				<div className="mt-6 flex h-10 items-center justify-center">
					<span className="text-xl font-medium text-muted-foreground">
						Use it to{" "}
						<span className="inline-block min-w-[14ch] text-left text-sky-400 font-semibold">
							{typewriterText}
							<span className="animate-pulse">|</span>
						</span>
					</span>
				</div>
				<div className="mt-8 flex flex-wrap items-center justify-center gap-3">
					<Button asChild size="lg">
						<Link to="/login">Get started</Link>
					</Button>
					<Button asChild variant="outline" size="lg">
						<a href="#features">
							See features <ArrowRight className="ml-1 size-4" />
						</a>
					</Button>
				</div>
			</div>
		</section>
	);
}
