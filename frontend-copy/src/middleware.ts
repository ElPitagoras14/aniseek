import { auth } from "@/auth";
import { getToken } from "next-auth/jwt";
import { NextResponse } from "next/server";

const AUTH_SECRET = process.env.AUTH_SECRET;

const unprotectedPaths = ["/login", "/register", "/"];

export default auth(async (req) => {
  const token = await getToken({
    req,
    secret: AUTH_SECRET,
  });

  const { pathname } = req.nextUrl;
  const baseUrl = req.nextUrl.origin;
  const username = token?.data?.user?.username;

  const isAuthenticated = token && token.error !== "RefreshTokenExpired";

  if (unprotectedPaths.includes(pathname) && !isAuthenticated) {
    console.log(`[MIDDLEWARE] [${username}] Unprotected path ${pathname}`);
    return NextResponse.next();
  }

  if (["/login", "/register"].includes(pathname)) {
    if (!isAuthenticated) {
      console.log(
        `[MIDDLEWARE] [${username}] No auth user in ${pathname}, allow the path`
      );
      return NextResponse.next();
    }

    console.log(`[MIDDLEWARE] [${username}] Auth user redirecting to home`);
    return NextResponse.redirect(`${baseUrl}/home`);
  }

  if (!isAuthenticated) {
    console.log(`[MIDDLEWARE] [${username}] No auth user redirecting to login`);
    return NextResponse.redirect(`${baseUrl}/login`);
  }

  console.log(`[MIDDLEWARE] [${username}] Auth user allowing the path`);
  return NextResponse.next();
});

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|.*\\.png$).*)"],
};
