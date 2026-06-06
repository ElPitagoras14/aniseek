import {
	createContext,
	useCallback,
	useContext,
	useMemo,
	useState,
} from "react";

interface User {
	username: string;
	role: string;
	isActive: boolean;
	avatarUrl: string | null;
	loginAt: number | null;
}

export interface AuthContext {
	isAuthenticated: boolean;
	login: (token: string) => void;
	logout: () => void;
	user: User | null;
}

const AuthContext = createContext<AuthContext | null>(null);

const key = "aniseek-auth";

function decodeToken(token: string): User | null {
	const parts = token.split(".");
	const payloadPart = parts[1];
	if (!payloadPart || parts.length !== 3) {
		return null;
	}
	try {
		const payload = JSON.parse(atob(payloadPart));
		return {
			username: payload.username,
			role: payload.role,
			isActive: payload.isActive ?? true,
			avatarUrl: payload.avatarUrl ?? null,
			loginAt: payload.iat ?? null,
		};
	} catch {
		return null;
	}
}

function getStoredUser(): User | null {
	const token = localStorage.getItem(key);
	if (!token) {
		return null;
	}

	const user = decodeToken(token);
	if (!user) {
		localStorage.removeItem(key);
	}
	return user;
}

function setStoredUser(user: string | null) {
	if (user) {
		localStorage.setItem(key, user);
	} else {
		localStorage.removeItem(key);
	}
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
	const [user, setUser] = useState<User | null>(() => getStoredUser());
	const isAuthenticated = !!user;

	const logout = useCallback(() => {
		setStoredUser(null);
		setUser(null);
		window.location.href = "/login";
	}, []);

	const login = useCallback((token: string) => {
		const user = decodeToken(token);
		if (!user) throw new Error("Invalid token");
		setStoredUser(token);
		setUser(user);
	}, []);

	const value = useMemo(
		() => ({ isAuthenticated, user, login, logout }),
		[isAuthenticated, user, login, logout],
	);

	return <AuthContext value={value}>{children}</AuthContext>;
}

export function useAuth() {
	const context = useContext(AuthContext);
	if (!context) {
		throw new Error("useAuth must be used within an AuthProvider");
	}
	return context;
}
