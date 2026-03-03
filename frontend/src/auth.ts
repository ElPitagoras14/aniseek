import NextAuth from "next-auth";
import axios from "axios";
import type {
  AuthValidity,
  BackendAccessJWT,
  BackendJWT,
  DecodedJWT,
  UserObject,
} from "next-auth";
import Credentials from "next-auth/providers/credentials";
import { jwtDecode } from "jwt-decode";
import type { JWT } from "next-auth/jwt";


const API_BASE_URL =
  process.env.NODE_ENV === "development"
    ? "http://localhost:4000/api/v1"
    : "http://nginx:80/api/v1";


export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [
    Credentials({
      name: "Login",
      credentials: {
        username: { label: "Username", type: "text" },
        password: { label: "Password", type: "password" },
      },
      authorize: async (credentials) => {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/login`, {
            username: credentials.username,
            password: credentials.password,
          });

          const tokens: BackendJWT = response.data.payload;

          const access: DecodedJWT = jwtDecode(tokens.access);
          const refresh: DecodedJWT = jwtDecode(tokens.refresh);

          const user: UserObject = {
            id: access.id,
            username: access.username,
            isActive: access.isActive,
            role: access.role,
            avatarUrl: access.avatarUrl,
            avatarLabel: access.avatarLabel,
          };

          const validity: AuthValidity = {
            validUntil: access.exp,
            refreshUntil: refresh.exp,
          };

          return {
            tokens,
            user,
            validity,
          };
        } catch (error) {
          console.error(error);
          return null;
        }
      },
    }),
  ],
  useSecureCookies: false,
  callbacks: {
    jwt: async ({ token, user, account, trigger }) => {
      if (user && account) {
        return { ...token, data: user };
      }

      if (trigger === "update") {
        try {
          const response = await axios.get(`${API_BASE_URL}/users/me`);
          const updatedUser = response.data.payload;

          token.data.user = {
            ...token.data.user,
            avatarUrl: updatedUser.avatarUrl,
            avatarLabel: updatedUser.avatarLabel,
            username: updatedUser.username,
            role: updatedUser.role,
          };
        } catch (error) {
          console.error("Error fetching updated user info:", error);
        }
      }

      if (Date.now() >= token.data.validity.refreshUntil * 1000) {
        return { ...token, error: "RefreshTokenExpired" } as JWT;
      }

      if (Date.now() < token.data.validity.validUntil * 1000) {
        return token;
      }

      if (Date.now() < token.data.validity.refreshUntil * 1000) {
        const response = await axios.post(`${API_BASE_URL}/auth/refresh`, null, {
          params: { refresh_token: token.data.tokens.refresh },
        });
        const newToken: BackendAccessJWT = response.data.payload;
        const { exp }: DecodedJWT = jwtDecode(newToken.access);
        token.data.validity.validUntil = Math.min(
          exp,
          token.data.validity.refreshUntil
        );
        token.data.tokens.access = newToken.access;
        return token;
      }

      return { ...token, error: "RefreshTokenExpired" } as JWT;
    },
    session: async ({ session, token }) => {
      const data = token.data;

      return {
        ...session,
        user: data.user,
        accessToken: data.tokens.access,
        validity: data.validity,
        error: token.error,
      };
    },
  },
  pages: {
    signIn: "/login",
  },
  trustHost: true,
});
