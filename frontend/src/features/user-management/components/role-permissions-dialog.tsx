import { CircleCheck, Minus, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogHeader,
	DialogTitle,
	DialogTrigger,
} from "@/components/ui/dialog";
import {
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableHeader,
	TableRow,
} from "@/components/ui/table";

// Hardcoded on purpose: roles are fixed and their permissions live in the
// backend code (require_role / assert_can_manage), not in a table. Keep this
// in sync with the access-control and user-administration specs.
type Level = true | false | "members";

interface Permission {
	label: string;
	owner: Level;
	admin: Level;
	member: Level;
}

const PERMISSIONS: Permission[] = [
	{
		label: "Browse, search and view anime and the calendar",
		owner: true,
		admin: true,
		member: true,
	},
	{
		label: "Save anime and request downloads",
		owner: true,
		admin: true,
		member: true,
	},
	{
		label: "View storage usage and franchises",
		owner: true,
		admin: true,
		member: true,
	},
	{
		label: "Edit own profile and password",
		owner: true,
		admin: true,
		member: true,
	},
	{
		label: "Delete downloaded files",
		owner: true,
		admin: true,
		member: false,
	},
	{ label: "Create franchises", owner: true, admin: true, member: false },
	{ label: "List users", owner: true, admin: true, member: false },
	{
		label: "Create, disable and reset the password of users",
		owner: true,
		admin: "members",
		member: false,
	},
	{
		label: "Create and revoke invitations",
		owner: true,
		admin: "members",
		member: false,
	},
	{
		label: "Change the registration policy",
		owner: true,
		admin: true,
		member: false,
	},
	{ label: "Change a user's role", owner: true, admin: false, member: false },
	{ label: "Transfer ownership", owner: true, admin: false, member: false },
];

function Cell({ level }: { level: Level }) {
	if (level === true) {
		return <CircleCheck className="mx-auto size-4 text-green-500" />;
	}
	if (level === "members") {
		return (
			<span className="block text-center text-xs text-muted-foreground">
				Members only
			</span>
		);
	}
	return <Minus className="mx-auto size-4 text-muted-foreground/50" />;
}

export function RolePermissionsDialog() {
	return (
		<Dialog>
			<DialogTrigger asChild>
				<Button variant="outline">
					<ShieldCheck />
					Role permissions
				</Button>
			</DialogTrigger>
			<DialogContent className="sm:max-w-2xl">
				<DialogHeader>
					<DialogTitle>Role permissions</DialogTitle>
					<DialogDescription>
						What each role can do on this instance. There is exactly one owner.
					</DialogDescription>
				</DialogHeader>
				<Table>
					<TableHeader>
						<TableRow>
							<TableHead>Action</TableHead>
							<TableHead className="w-24 text-center">Owner</TableHead>
							<TableHead className="w-24 text-center">Admin</TableHead>
							<TableHead className="w-24 text-center">Member</TableHead>
						</TableRow>
					</TableHeader>
					<TableBody>
						{PERMISSIONS.map((permission) => (
							<TableRow key={permission.label}>
								<TableCell className="whitespace-normal">
									{permission.label}
								</TableCell>
								<TableCell>
									<Cell level={permission.owner} />
								</TableCell>
								<TableCell>
									<Cell level={permission.admin} />
								</TableCell>
								<TableCell>
									<Cell level={permission.member} />
								</TableCell>
							</TableRow>
						))}
					</TableBody>
				</Table>
			</DialogContent>
		</Dialog>
	);
}
