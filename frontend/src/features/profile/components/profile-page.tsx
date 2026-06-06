import { Card, CardContent } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { PasswordSection } from "./password-section";
import { ProfileInfoCard } from "./profile-info-card";
import { UsernameSection } from "./username-section";

export function ProfilePage() {

	return (
		<div className="flex flex-col gap-6 p-4 md:p-6 lg:p-8">
			<div>
				<h1 className="text-2xl font-bold">Profile</h1>
				<p className="text-sm text-muted-foreground">
					Manage your account settings and security
				</p>
			</div>

			<div className="grid gap-6 lg:grid-cols-[5fr_7fr]">
				<ProfileInfoCard />

				<Card>
					<CardContent className="flex flex-col gap-5 p-6">
						<div>
							<p className="text-base font-semibold">Account settings</p>
							<p className="text-sm text-muted-foreground">
								Update your account information and password
							</p>
						</div>

						<div className="flex flex-col gap-3">
							<div className="flex flex-col gap-1.5">
								<p className="text-sm">Username</p>
								<UsernameSection />
							</div>
						</div>

						<Separator />

						<div className="flex flex-col gap-3">
							<PasswordSection />
						</div>
					</CardContent>
				</Card>
			</div>
		</div>
	);
}
