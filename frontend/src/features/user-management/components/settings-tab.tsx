import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Check, Globe, Mail, UserPlus } from "lucide-react";
import { toast } from "sonner";
import {
	settingsQueryOptions,
	updateRegistrationPolicy,
} from "@/features/access/api";
import { parseApiError } from "@/features/access/lib/parse-error";
import type { AccessUser, RegistrationPolicy } from "@/features/access/types";
import { cn } from "@/lib/utils";
import { SettingsSection } from "./settings-section";
import { TransferOwnerCard } from "./transfer-owner-card";

const POLICY_OPTIONS: {
	value: RegistrationPolicy;
	icon: typeof Mail;
	title: string;
	description: string;
}[] = [
	{
		value: "invite",
		icon: Mail,
		title: "Invitation only",
		description: "Only people with an invitation link can create an account.",
	},
	{
		value: "open",
		icon: Globe,
		title: "Open to anyone",
		description: "Anyone who can reach the instance can sign up as a member.",
	},
];

export function SettingsTab({ me }: { me: AccessUser }) {
	const queryClient = useQueryClient();
	const settings = useQuery(settingsQueryOptions);
	const current = settings.data?.registrationPolicy;

	const mutation = useMutation({
		mutationFn: updateRegistrationPolicy,
		onSuccess: () => {
			queryClient.invalidateQueries({
				queryKey: settingsQueryOptions.queryKey,
			});
			queryClient.invalidateQueries({ queryKey: ["auth", "registration"] });
			toast.success("Registration policy updated");
		},
		onError: (error) => {
			toast.error(parseApiError(error, "Could not update the policy"));
		},
	});

	return (
		<div
			className={cn(
				"grid items-stretch gap-6",
				me.role === "owner" && "lg:grid-cols-2",
			)}
		>
			<SettingsSection
				icon={UserPlus}
				title="Registration"
				description="Who can sign up without an invitation."
			>
				<fieldset className="flex flex-col gap-3">
					<legend className="sr-only">Registration policy</legend>
					{POLICY_OPTIONS.map((option) => {
						const selected = current === option.value;
						return (
							<label
								key={option.value}
								className={cn(
									"flex cursor-pointer items-start gap-3 rounded-lg border p-4 transition-colors",
									"hover:bg-muted/40 has-focus-visible:ring-2 has-focus-visible:ring-ring has-disabled:cursor-not-allowed has-disabled:opacity-60",
									selected && "border-primary bg-primary/5 ring-1 ring-primary",
								)}
							>
								<input
									type="radio"
									name="registration-policy"
									className="sr-only"
									checked={selected}
									disabled={!current || mutation.isPending}
									onChange={() => mutation.mutate(option.value)}
								/>
								<option.icon
									className={cn(
										"mt-0.5 size-5 shrink-0",
										selected ? "text-primary" : "text-muted-foreground",
									)}
								/>
								<span className="flex min-w-0 flex-1 flex-col gap-1">
									<span className="text-sm font-medium">{option.title}</span>
									<span className="text-xs text-muted-foreground">
										{option.description}
									</span>
								</span>
								<span
									className={cn(
										"flex size-5 shrink-0 items-center justify-center rounded-full border",
										selected
											? "border-primary bg-primary text-primary-foreground"
											: "border-muted-foreground/40",
									)}
								>
									{selected && <Check className="size-3" />}
								</span>
							</label>
						);
					})}
				</fieldset>
			</SettingsSection>

			{me.role === "owner" && <TransferOwnerCard />}
		</div>
	);
}
