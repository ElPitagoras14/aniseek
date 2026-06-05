import { Eye, EyeOff, Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useLogin } from "@/features/auth/hooks/use-login";

export function LoginForm() {
	const {
		username,
		setUsername,
		password,
		setPassword,
		showPassword,
		setShowPassword,
		isPending,
		handleSubmit,
	} = useLogin();

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
						autoComplete="current-password"
						required
						placeholder="Password"
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
			<Button type="submit" disabled={isPending} className="w-full">
				{isPending && <Loader2 className="mr-2 size-4 animate-spin" />}
				Login
			</Button>
		</form>
	);
}
