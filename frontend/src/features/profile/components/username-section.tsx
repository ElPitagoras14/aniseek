import { Loader2 } from "lucide-react";
import { useAuth } from "@/auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useUpdateUsername } from "../hooks/use-update-username";

export function UsernameSection() {
	const { user } = useAuth();
	const { form, isPending } = useUpdateUsername();

	return (
		<form
			onSubmit={(e) => {
				e.preventDefault();
				e.stopPropagation();
				form.handleSubmit();
			}}
		>
			<form.Field name="username">
				{(field) => (
					<div className="flex flex-col gap-1">
						<div className="flex gap-2">
							<Input
								id="username"
								name="username"
								type="text"
								autoComplete="username"
								value={field.state.value}
								onChange={(e) => field.handleChange(e.target.value)}
								onBlur={field.handleBlur}
								disabled={isPending}
								className="flex-1"
							/>
							<form.Subscribe
								selector={(s) => [s.canSubmit, s.isSubmitting] as const}
							>
								{([canSubmit, isSubmitting]) => {
									const isModified =
										field.state.value !== (user?.username ?? "");
									return (
										<Button
											type="submit"
											disabled={!canSubmit || !isModified || isPending}
										>
											{(isSubmitting || isPending) && (
												<Loader2 className="mr-1.5 size-4 animate-spin" />
											)}
											Update
										</Button>
									);
								}}
							</form.Subscribe>
						</div>
						{field.state.meta.errors.filter(Boolean).map((err) => {
							const message = typeof err === "string" ? err : err.message;
							return (
								<p key={message} className="text-xs text-destructive">
									{message}
								</p>
							);
						})}
					</div>
				)}
			</form.Field>
		</form>
	);
}
