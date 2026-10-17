import { Eye, EyeOff, Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useRegister } from "../hooks/use-register";

export function RegisterForm({
	invitationToken,
}: {
	invitationToken: string | undefined;
}) {
	const {
		username,
		setUsername,
		password,
		setPassword,
		confirm,
		setConfirm,
		showPassword,
		setShowPassword,
		isPending,
		handleSubmit,
	} = useRegister(invitationToken);

	return (
		<form onSubmit={handleSubmit} className="flex flex-col gap-4">
			<div className="flex flex-col gap-2">
				<Label htmlFor="username">Username</Label>
				<Input
					id="username"
					name="username"
					type="text"
					autoComplete="username"
					required
					maxLength={64}
					placeholder="Username"
					value={username}
					onChange={(e) => setUsername(e.target.value)}
					disabled={isPending}
				/>
			</div>
			<div className="flex flex-col gap-2">
				<Label htmlFor="password">Password</Label>
				<div className="relative">
					<Input
						id="password"
						name="password"
						type={showPassword ? "text" : "password"}
						autoComplete="new-password"
						required
						placeholder="At least 6 characters"
						value={password}
						onChange={(e) => setPassword(e.target.value)}
						disabled={isPending}
						className="pr-10"
					/>
					<Button
						type="button"
						variant="ghost"
						size="icon"
						onClick={() => setShowPassword((s) => !s)}
						className="absolute right-0 top-0 h-full px-3"
						aria-label={showPassword ? "Hide password" : "Show password"}
					>
						{showPassword ? (
							<EyeOff className="size-4" />
						) : (
							<Eye className="size-4" />
						)}
					</Button>
				</div>
			</div>
			<div className="flex flex-col gap-2">
				<Label htmlFor="confirm">Confirm password</Label>
				<Input
					id="confirm"
					name="confirm"
					type={showPassword ? "text" : "password"}
					autoComplete="new-password"
					required
					placeholder="Repeat the password"
					value={confirm}
					onChange={(e) => setConfirm(e.target.value)}
					disabled={isPending}
				/>
			</div>
			<Button type="submit" disabled={isPending} className="w-full">
				{isPending && <Loader2 className="mr-2 size-4 animate-spin" />}
				Create account
			</Button>
		</form>
	);
}
