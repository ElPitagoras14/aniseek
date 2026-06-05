export interface LoginPayload {
	username: string;
	password: string;
}

export interface LoginResponse {
	status: string;
	message: string;
	payload: { access: string; refresh: string };
	statusCode: number;
}
