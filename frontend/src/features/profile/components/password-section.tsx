import { useState } from "react";
import { Eye, EyeOff, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useUpdatePassword } from "../hooks/use-update-password";

export function PasswordSection() {
	const [showCurrent, setShowCurrent] = useState(false);
	const [showNew, setShowNew] = useState(false);
	const [showConfirm, setShowConfirm] = useState(false);

	const { form, isPending } = useUpdatePassword();

	return (
		<form
			onSubmit={(e) => {
				e.preventDefault();
				e.stopPropagation();
				form.handleSubmit();
			}}
			className="flex flex-col gap-4"
		>
			<form.Field name="currentPassword">
				{(field) => (
					<div className="flex flex-col gap-1.5">
						<Label htmlFor="currentPassword">Current password</Label>
						<div className="relative">
							<Input
								id="currentPassword"
								name="currentPassword"
								type={showCurrent ? "text" : "password"}
								autoComplete="current-password"
								value={field.state.value}
								onChange={(e) => field.handleChange(e.target.value)}
								onBlur={field.handleBlur}
								disabled={isPending}
								className="pr-10"
							/>
							<Button
								type="button"
								variant="ghost"
								size="icon"
								onClick={() => setShowCurrent((s) => !s)}
								className="absolute right-0 top-0 h-full px-3"
								aria-label={showCurrent ? "Hide" : "Show"}
							>
								{showCurrent ? (
									<EyeOff className="size-4" />
								) : (
									<Eye className="size-4" />
								)}
							</Button>
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

			<form.Field name="newPassword">
				{(field) => (
					<div className="flex flex-col gap-1.5">
						<Label htmlFor="newPassword">New password</Label>
						<div className="relative">
							<Input
								id="newPassword"
								name="newPassword"
								type={showNew ? "text" : "password"}
								autoComplete="new-password"
								value={field.state.value}
								onChange={(e) => field.handleChange(e.target.value)}
								onBlur={field.handleBlur}
								disabled={isPending}
								className="pr-10"
							/>
							<Button
								type="button"
								variant="ghost"
								size="icon"
								onClick={() => setShowNew((s) => !s)}
								className="absolute right-0 top-0 h-full px-3"
								aria-label={showNew ? "Hide" : "Show"}
							>
								{showNew ? (
									<EyeOff className="size-4" />
								) : (
									<Eye className="size-4" />
								)}
							</Button>
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

			<form.Field
				name="confirmPassword"
				validators={{
					onChangeListenTo: ["newPassword"],
					onChange: ({ value, fieldApi }) => {
						if (
							value &&
							value !== fieldApi.form.getFieldValue("newPassword")
						) {
							return "Passwords do not match";
						}
						return undefined;
					},
				}}
			>
				{(field) => (
					<div className="flex flex-col gap-1.5">
						<Label htmlFor="confirmPassword">Confirm new password</Label>
						<div className="relative">
							<Input
								id="confirmPassword"
								name="confirmPassword"
								type={showConfirm ? "text" : "password"}
								autoComplete="new-password"
								value={field.state.value}
								onChange={(e) => field.handleChange(e.target.value)}
								onBlur={field.handleBlur}
								disabled={isPending}
								className="pr-10"
							/>
							<Button
								type="button"
								variant="ghost"
								size="icon"
								onClick={() => setShowConfirm((s) => !s)}
								className="absolute right-0 top-0 h-full px-3"
								aria-label={showConfirm ? "Hide" : "Show"}
							>
								{showConfirm ? (
									<EyeOff className="size-4" />
								) : (
									<Eye className="size-4" />
								)}
							</Button>
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

			<form.Subscribe
				selector={(s) => [s.canSubmit, s.isSubmitting, s.isDirty] as const}
			>
				{([canSubmit, isSubmitting, isDirty]) => (
					<div className="flex justify-end gap-2 pt-2">
						<Button
							type="button"
							variant="outline"
							disabled={!isDirty || isPending}
							onClick={() => form.reset()}
						>
							Cancel
						</Button>
						<Button type="submit" disabled={!canSubmit || isPending}>
							{(isSubmitting || isPending) && (
								<Loader2 className="mr-1.5 size-4 animate-spin" />
							)}
							Save changes
						</Button>
					</div>
				)}
			</form.Subscribe>
		</form>
	);
}
